"""
Security utilities for authentication and authorization.

Provides JWT token verification, user authentication dependencies,
role-based access control, and rate limiting configuration.
"""

from typing import Any, Callable, Dict, List, Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError as JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.logging import get_logger
from app.core.supabase_client import get_supabase_admin

logger = get_logger(__name__)

# HTTP Bearer scheme for Swagger UI integration
bearer_scheme = HTTPBearer(auto_error=False)

# Rate limiter instance using client IP
limiter = Limiter(key_func=get_remote_address)

# Cached PyJWKClient instance for Supabase JWKS verification
_jwks_client: Optional[PyJWKClient] = None


def get_jwks_client() -> PyJWKClient:
    """Return cached PyJWKClient instance for Supabase JWKS verification."""
    global _jwks_client
    if _jwks_client is None:
        settings = get_settings()
        jwks_url = settings.jwks_url
        if not jwks_url:
            logger.error("jwks_url_not_configured")
            raise UnauthorizedError("Authentication configuration error: Supabase JWKS URL is not configured")
        _jwks_client = PyJWKClient(
            jwks_url,
            cache_keys=True,
            cache_jwk_set=True,
            lifespan=3600,
            timeout=10,
        )
    return _jwks_client


def set_jwks_client(client: Optional[Any]) -> None:
    """Allow overriding or mocking the JWKS client (primarily for testing)."""
    global _jwks_client
    _jwks_client = client


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify a JWT token issued by Supabase Auth.

    Supports:
    1. ES256 (ECC P-256) asymmetric signatures verified against Supabase JWKS.
    2. HS256 symmetric signatures verified against JWT_SECRET (backward compatibility).

    Validates:
    - Cryptographic signature (never disabled)
    - Expiration (exp)
    - Audience (aud == 'authenticated')
    - Issuer (iss matches Supabase project auth endpoint)
    - Subject (sub exists and is non-empty)

    Args:
        token: The raw JWT token string.

    Returns:
        Dictionary containing decoded token payload with at least 'sub' (user_id).

    Raises:
        UnauthorizedError: If the token is invalid, expired, malformed, or untrusted.
    """
    if not token or not isinstance(token, str) or not token.strip():
        raise UnauthorizedError("Authentication token is required")

    token = token.strip()
    settings = get_settings()

    # Step 1: Parse unverified header to determine algorithm
    try:
        header = jwt.get_unverified_header(token)
    except Exception as e:
        logger.warning("token_header_parse_failed", error=str(e))
        raise UnauthorizedError(f"Malformed authentication token: {str(e)}")

    alg = header.get("alg")
    if not alg:
        raise UnauthorizedError("Invalid token: missing 'alg' in token header")

    if alg not in settings.JWT_ALGORITHMS:
        logger.warning("unsupported_jwt_algorithm", alg=alg, allowed=settings.JWT_ALGORITHMS)
        raise UnauthorizedError(
            f"Unsupported signing algorithm '{alg}'. Only {', '.join(settings.JWT_ALGORITHMS)} are allowed."
        )

    payload: Dict[str, Any]

    # Step 2: Verify signature based on algorithm
    if alg == "ES256":
        jwk_client = get_jwks_client()
        try:
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            key = signing_key.key
        except Exception as e:
            logger.warning("jwks_key_fetch_failed", error=str(e))
            raise UnauthorizedError(f"Unable to verify token signature: public key retrieval failed ({str(e)})")

        try:
            payload = jwt.decode(
                token,
                key,
                algorithms=["ES256"],
                audience="authenticated",
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": True,
                },
            )
        except JWTError as e:
            logger.warning("es256_token_verification_failed", error=str(e))
            raise UnauthorizedError(f"Invalid or expired token: {str(e)}")

    elif alg == "HS256":
        if not settings.JWT_SECRET or not settings.JWT_SECRET.strip():
            logger.error("jwt_secret_not_configured_for_hs256")
            raise UnauthorizedError("Authentication configuration error: JWT_SECRET is not configured for HS256 verification")

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": True,
                },
            )
        except JWTError as e:
            logger.warning("hs256_token_verification_failed", error=str(e))
            raise UnauthorizedError(f"Invalid or expired token: {str(e)}")
    else:
        raise UnauthorizedError(f"Unsupported signing algorithm '{alg}'")

    # Step 3: Validate issuer (iss)
    expected_issuer = settings.auth_issuer.rstrip("/") if settings.auth_issuer else ""
    token_issuer = payload.get("iss")
    if expected_issuer:
        if token_issuer:
            if token_issuer.rstrip("/") != expected_issuer:
                logger.warning("token_issuer_mismatch", expected=expected_issuer, actual=token_issuer)
                raise UnauthorizedError(f"Invalid token issuer: expected '{expected_issuer}', got '{token_issuer}'")
        elif alg == "ES256":
            logger.warning("es256_token_missing_issuer")
            raise UnauthorizedError("Invalid token: missing issuer claim")

    # Step 4: Validate subject (sub)
    user_id = payload.get("sub")
    if not user_id or not isinstance(user_id, str) or not user_id.strip():
        raise UnauthorizedError("Invalid token: missing or invalid user identifier ('sub')")

    return payload


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """
    FastAPI dependency that extracts and verifies the current user.

    Reads the Bearer token from the Authorization header, verifies it,
    then fetches the full user profile from the database.

    Args:
        request: The incoming FastAPI request.
        credentials: The extracted HTTP Bearer credentials.

    Returns:
        Dictionary containing the user's profile data including id, email,
        full_name, role, city, area, and other profile fields.

    Raises:
        UnauthorizedError: If no token is provided or token is invalid.
    """
    if credentials is None:
        raise UnauthorizedError("Authentication required. Please provide a Bearer token.")

    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload["sub"]

    # Fetch user profile from database
    supabase = get_supabase_admin()
    try:
        result = supabase.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
    except Exception as e:
        logger.error("profile_fetch_error", user_id=user_id, error=str(e))
        raise UnauthorizedError("Unable to verify user profile")

    if result is None or result.data is None:
        logger.warning("profile_not_found", user_id=user_id)
        raise UnauthorizedError("User profile not found. Please complete registration.")

    user_profile = result.data
    user_profile["id"] = user_id

    # Check if account is active
    if not user_profile.get("is_active", True):
        logger.warning("deactivated_user_access", user_id=user_id)
        raise ForbiddenError("Account has been deactivated. Please contact administration.")

    # Store user in request state for downstream access
    request.state.user = user_profile
    return user_profile


def require_role(*roles: str) -> Callable:
    """
    Dependency factory that enforces role-based access control.

    Creates a FastAPI dependency that checks whether the authenticated
    user has one of the specified roles.

    Args:
        *roles: One or more role strings (e.g., 'admin', 'donor', 'patient', 'blood_bank').

    Returns:
        An async dependency function that returns the user profile if authorized.

    Raises:
        ForbiddenError: If the user's role is not in the allowed roles.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user=Depends(require_role("admin"))):
            ...
    """

    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        """Check if the current user has the required role."""
        user_role = current_user.get("role", "")
        if user_role not in roles:
            logger.warning(
                "access_denied",
                user_id=current_user.get("id"),
                user_role=user_role,
                required_roles=list(roles),
            )
            raise ForbiddenError(
                f"This action requires one of the following roles: {', '.join(roles)}. "
                f"Your role is '{user_role}'."
            )
        return current_user

    return role_checker


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency that optionally extracts user info.

    Returns the user profile if a valid token is provided, or None
    if no token is present. Does not raise on missing token.

    Returns:
        User profile dict or None.
    """
    if credentials is None:
        return None

    try:
        payload = verify_token(credentials.credentials)
        user_id = payload["sub"]
        supabase = get_supabase_admin()
        result = supabase.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
        if result and result.data:
            profile = result.data
            if not profile.get("is_active", True):
                return None
            profile["id"] = user_id
            return profile
    except Exception:
        pass

    return None
