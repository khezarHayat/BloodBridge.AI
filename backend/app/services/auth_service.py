"""
Authentication service.

Handles user registration, login, profile retrieval, and profile updates
using Supabase Auth and the profiles database table.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError, ValidationError
from app.core.logging import get_logger
from app.core.supabase_client import get_supabase_admin, get_supabase_client
from app.schemas.auth import LoginRequest, ProfileUpdateRequest, RegisterRequest

logger = get_logger(__name__)


async def register_user(data: RegisterRequest) -> Dict[str, Any]:
    """
    Register a new user in the system.

    Creates the user in Supabase Auth, then creates a profile record
    and a role-specific record (donor or blood_bank) in the database.

    Args:
        data: Registration request data.

    Returns:
        Dictionary with access_token and user profile.

    Raises:
        ValidationError: If role is unauthorized or registration fails.
        ConflictError: If email is already registered.
    """
    if data.role in ["admin", "hospital"]:
        raise ValidationError(f"Registration for '{data.role}' role is prohibited. Institutional accounts require administrator provisioning.")

    supabase = get_supabase_client()
    admin_client = get_supabase_admin()

    # Step 1: Create user in Supabase Auth
    try:
        auth_response = supabase.auth.sign_up(
            {
                "email": data.email,
                "password": data.password,
                "options": {
                    "data": {
                        "full_name": data.full_name,
                        "role": data.role,
                    }
                },
            }
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "already registered" in error_msg or "already exists" in error_msg:
            raise ConflictError("A user with this email already exists")
        logger.error("auth_signup_failed", email=data.email, error=str(e))
        raise ValidationError(f"Registration failed: {str(e)}")

    if not auth_response.user:
        raise ValidationError("Registration failed: no user returned from auth provider")

    user_id = auth_response.user.id
    access_token = ""
    if auth_response.session:
        access_token = auth_response.session.access_token

    # Step 2: Create profile record idempotently (handles database trigger pre-creation)
    now = datetime.now(timezone.utc).isoformat()

    existing_profile = None
    try:
        existing_res = (
            admin_client.table("profiles")
            .select("id, role, is_verified, created_at")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        if existing_res and existing_res.data:
            existing_profile = existing_res.data
    except Exception as e:
        logger.warning("profile_lookup_before_upsert_failed", error=str(e))

    # Protect against demoting or overriding verified status/roles
    target_role = data.role
    is_verified = False
    if existing_profile:
        is_verified = existing_profile.get("is_verified", False)
        if existing_profile.get("role") in ["admin", "hospital"]:
            target_role = existing_profile["role"]

    profile_data = {
        "id": user_id,
        "email": data.email,
        "full_name": data.full_name,
        "phone": data.phone,
        "role": target_role,
        "city": data.city,
        "area": data.area,
        "is_verified": is_verified,
        "is_active": True,
        "updated_at": now,
    }
    if not existing_profile or not existing_profile.get("created_at"):
        profile_data["created_at"] = now

    try:
        admin_client.table("profiles").upsert(profile_data, on_conflict="id").execute()
        logger.info("profile_provisioned", user_id=user_id, role=target_role)
    except Exception as e:
        logger.error("profile_creation_failed", user_id=user_id, error=str(e))
        # Try to clean up the auth user on failure
        try:
            admin_client.auth.admin.delete_user(user_id)
        except Exception:
            pass
        raise ValidationError(f"Failed to create user profile: {str(e)}")

    # Step 3: Create role-specific record idempotently
    if target_role == "donor":
        if not data.blood_group:
            raise ValidationError("Donor registration requires an explicit blood group")
        try:
            donor_data = {
                "user_id": user_id,
                "blood_group": data.blood_group,
                "is_available": True,
                "total_donations": 0,
                "availability_radius_km": 25.0,
                "consent_notifications": True,
                "created_at": now,
            }
            admin_client.table("donors").upsert(donor_data, on_conflict="user_id").execute()
            logger.info("donor_record_created", user_id=user_id, blood_group=data.blood_group)
        except Exception as e:
            logger.error("donor_record_creation_failed", user_id=user_id, error=str(e))

    elif target_role == "blood_bank":
        try:
            bank_data = {
                "user_id": user_id,
                "name": f"{data.full_name} Blood Bank",
                "license_number": "PENDING",
                "type": "blood_bank",
                "phone": data.phone,
                "address": data.area,
                "city": data.city,
                "area": data.area,
                "is_verified": False,
                "created_at": now,
            }
            admin_client.table("blood_banks").upsert(bank_data, on_conflict="user_id").execute()
            logger.info("blood_bank_record_created", user_id=user_id)
        except Exception as e:
            logger.error("blood_bank_record_creation_failed", user_id=user_id, error=str(e))

    user_profile = {
        "id": user_id,
        "email": data.email,
        "full_name": data.full_name,
        "phone": data.phone,
        "role": data.role,
        "city": data.city,
        "area": data.area,
        "avatar_url": None,
        "is_verified": False,
        "created_at": now,
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_profile,
    }


async def login_user(data: LoginRequest) -> Dict[str, Any]:
    """
    Authenticate a user and return a session token.

    Args:
        data: Login request data with email and password.

    Returns:
        Dictionary with access_token and user profile.

    Raises:
        UnauthorizedError: If credentials are invalid.
    """
    supabase = get_supabase_client()
    admin_client = get_supabase_admin()

    try:
        auth_response = supabase.auth.sign_in_with_password(
            {
                "email": data.email,
                "password": data.password,
            }
        )
    except Exception as e:
        logger.warning("login_failed", email=data.email, error=str(e))
        raise UnauthorizedError("Invalid email or password")

    if not auth_response.user or not auth_response.session:
        raise UnauthorizedError("Invalid email or password")

    user_id = auth_response.user.id
    access_token = auth_response.session.access_token

    # Fetch full profile from database
    profile_result = (
        admin_client.table("profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    if profile_result and profile_result.data:
        user_profile = profile_result.data
        user_profile["id"] = user_id
    else:
        # Fallback if profile doesn't exist yet (never trust user_metadata for role)
        app_meta = getattr(auth_response.user, "app_metadata", None) or {}
        app_meta_role = app_meta.get("role") if isinstance(app_meta, dict) else None
        safe_role = app_meta_role if app_meta_role in ["donor", "patient", "blood_bank", "hospital"] else "patient"

        user_meta = getattr(auth_response.user, "user_metadata", None) or {}
        full_name = user_meta.get("full_name", "") if isinstance(user_meta, dict) else ""

        user_profile = {
            "id": user_id,
            "email": data.email,
            "full_name": full_name,
            "phone": None,
            "role": safe_role,
            "city": None,
            "area": None,
            "avatar_url": None,
            "is_verified": False,
            "created_at": None,
        }

    logger.info("user_logged_in", user_id=user_id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_profile,
    }


async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Fetch a user's profile from the database.

    Args:
        user_id: The user's UUID.

    Returns:
        User profile dictionary.

    Raises:
        NotFoundError: If the profile does not exist.
    """
    supabase = get_supabase_admin()

    result = (
        supabase.table("profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    if not result or not result.data:
        raise NotFoundError("User profile", user_id)

    profile = result.data
    profile["id"] = user_id
    return profile


async def update_user_profile(user_id: str, data: ProfileUpdateRequest) -> Dict[str, Any]:
    """
    Update a user's profile in the database.

    Only updates fields that are provided (non-None).

    Args:
        user_id: The user's UUID.
        data: Profile update request data.

    Returns:
        Updated user profile dictionary.

    Raises:
        NotFoundError: If the profile does not exist.
    """
    supabase = get_supabase_admin()

    # Build update dict with only non-None fields
    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        return await get_user_profile(user_id)

    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    try:
        result = (
            supabase.table("profiles")
            .update(update_data)
            .eq("id", user_id)
            .execute()
        )
    except Exception as e:
        logger.error("profile_update_failed", user_id=user_id, error=str(e))
        raise ValidationError(f"Failed to update profile: {str(e)}")

    if not result or not result.data:
        raise NotFoundError("User profile", user_id)

    profile = result.data[0]
    profile["id"] = user_id
    logger.info("profile_updated", user_id=user_id, updated_fields=list(update_data.keys()))

    return profile


async def logout_user(access_token: str) -> None:
    """
    Invalidate a user's session.

    Args:
        access_token: The JWT access token to invalidate.
    """
    supabase = get_supabase_client()
    try:
        supabase.auth.sign_out()
        logger.info("user_logged_out")
    except Exception as e:
        logger.warning("logout_failed", error=str(e))


async def request_password_reset(email: str) -> None:
    """
    Send a password reset email to the user.

    Args:
        email: The user's email address.
    """
    supabase = get_supabase_client()
    try:
        supabase.auth.reset_password_email(email)
        logger.info("password_reset_requested", email=email)
    except Exception as e:
        logger.error("password_reset_failed", email=email, error=str(e))
        # Don't reveal whether the email exists
