"""
Unit tests for BloodBridge dual-algorithm JWT verification.

Validates:
1. Supabase ES256 (ECC P-256) signature verification via JWKS.
2. Backward-compatible HS256 signature verification via JWT_SECRET.
3. Cryptographic signature tampering detection (never disabled).
4. Expiration claim (exp) enforcement.
5. Audience claim (aud == 'authenticated') enforcement.
6. Issuer claim (iss) validation against Supabase Auth endpoint.
7. Subject claim (sub) presence and validity.
8. Rejection of forbidden algorithms ('none', 'RS256', etc.).
"""

import base64
import time
from typing import Any, Dict
import pytest
import jwt
from jwt import PyJWK
from cryptography.hazmat.primitives.asymmetric import ec

from app.core.config import Settings
from app.core.exceptions import UnauthorizedError
from app.core.security import set_jwks_client, verify_token


def b64url(val: int) -> str:
    """Helper to convert integer coordinate to base64url string."""
    b = val.to_bytes((val.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(b).decode("utf-8").rstrip("=")


class MockJWKClient:
    """Mock PyJWKClient that resolves keys from a local JWK dictionary."""

    def __init__(self, jwk_dict: Dict[str, Any]):
        self.jwk = PyJWK(jwk_dict)
        self.kid = jwk_dict.get("kid")

    def get_signing_key_from_jwt(self, token: str) -> PyJWK:
        header = jwt.get_unverified_header(token)
        if header.get("kid") == self.kid:
            return self.jwk
        raise Exception(f"Key ID '{header.get('kid')}' not found in mock JWKS")


@pytest.fixture(autouse=True)
def setup_jwt_environment(monkeypatch):
    """Set up test environment variables and clean up JWKS client."""
    test_settings = Settings(
        SUPABASE_URL="https://zkpunneykkcegvfibcrm.supabase.co",
        JWT_SECRET="test-super-secret-jwt-key-minimum-32-chars-long",
        JWT_ALGORITHM="ES256",
        JWT_ALGORITHMS=["ES256", "HS256"],
    )
    monkeypatch.setattr("app.core.security.get_settings", lambda: test_settings)
    yield
    set_jwks_client(None)


@pytest.fixture
def ec_key_pair():
    """Generate an EC P-256 key pair for ES256 tests."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    numbers = public_key.public_numbers()

    jwk_dict = {
        "kty": "EC",
        "crv": "P-256",
        "x": b64url(numbers.x),
        "y": b64url(numbers.y),
        "kid": "supabase-test-key-2026",
        "alg": "ES256",
        "use": "sig",
    }
    return private_key, public_key, jwk_dict


# ==========================================
# 1. ES256 (Supabase JWKS) Tests
# ==========================================

def test_verify_valid_es256_token(ec_key_pair):
    """Verify valid ES256 token signed with EC P-256 key against JWKS."""
    private_key, _, jwk_dict = ec_key_pair
    set_jwks_client(MockJWKClient(jwk_dict))

    now = int(time.time())
    payload = {
        "sub": "user_es256_test_uuid",
        "aud": "authenticated",
        "iss": "https://zkpunneykkcegvfibcrm.supabase.co/auth/v1",
        "iat": now,
        "exp": now + 3600,
        "email": "donor@example.com",
        "role": "donor",
    }
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers={"kid": "supabase-test-key-2026", "typ": "JWT"},
    )

    verified = verify_token(token)
    assert verified["sub"] == "user_es256_test_uuid"
    assert verified["email"] == "donor@example.com"
    assert verified["role"] == "donor"


def test_es256_forged_signature_rejected(ec_key_pair):
    """Verify ES256 token signed by an unauthorized key is rejected."""
    _, _, jwk_dict = ec_key_pair
    set_jwks_client(MockJWKClient(jwk_dict))

    # Attacker signs with different EC key
    attacker_key = ec.generate_private_key(ec.SECP256R1())
    token = jwt.encode(
        {"sub": "attacker", "aud": "authenticated", "iss": "https://zkpunneykkcegvfibcrm.supabase.co/auth/v1"},
        attacker_key,
        algorithm="ES256",
        headers={"kid": "supabase-test-key-2026"},
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token(token)
    assert "Invalid or expired token" in str(exc_info.value)


def test_es256_expired_token_rejected(ec_key_pair):
    """Verify expired ES256 token is rejected."""
    private_key, _, jwk_dict = ec_key_pair
    set_jwks_client(MockJWKClient(jwk_dict))

    past = int(time.time()) - 100
    token = jwt.encode(
        {
            "sub": "user_expired",
            "aud": "authenticated",
            "iss": "https://zkpunneykkcegvfibcrm.supabase.co/auth/v1",
            "exp": past,
        },
        private_key,
        algorithm="ES256",
        headers={"kid": "supabase-test-key-2026"},
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token(token)
    assert "expired" in str(exc_info.value).lower()


def test_es256_invalid_audience_rejected(ec_key_pair):
    """Verify token with wrong audience is rejected."""
    private_key, _, jwk_dict = ec_key_pair
    set_jwks_client(MockJWKClient(jwk_dict))

    token = jwt.encode(
        {
            "sub": "user_wrong_aud",
            "aud": "wrong_audience",
            "iss": "https://zkpunneykkcegvfibcrm.supabase.co/auth/v1",
        },
        private_key,
        algorithm="ES256",
        headers={"kid": "supabase-test-key-2026"},
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token(token)
    assert "audience" in str(exc_info.value).lower()


def test_es256_invalid_issuer_rejected(ec_key_pair):
    """Verify token with wrong issuer is rejected."""
    private_key, _, jwk_dict = ec_key_pair
    set_jwks_client(MockJWKClient(jwk_dict))

    token = jwt.encode(
        {
            "sub": "user_wrong_iss",
            "aud": "authenticated",
            "iss": "https://malicious-project.supabase.co/auth/v1",
        },
        private_key,
        algorithm="ES256",
        headers={"kid": "supabase-test-key-2026"},
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token(token)
    assert "issuer" in str(exc_info.value).lower()


def test_es256_unknown_kid_rejected(ec_key_pair):
    """Verify token with unknown kid raises UnauthorizedError."""
    private_key, _, jwk_dict = ec_key_pair
    set_jwks_client(MockJWKClient(jwk_dict))

    token = jwt.encode(
        {"sub": "user_1", "aud": "authenticated", "iss": "https://zkpunneykkcegvfibcrm.supabase.co/auth/v1"},
        private_key,
        algorithm="ES256",
        headers={"kid": "non_existent_key_id"},
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token(token)
    assert "public key retrieval failed" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()


# ==========================================
# 2. HS256 (Backward Compatibility) Tests
# ==========================================

def test_verify_valid_hs256_token():
    """Verify backward-compatible HS256 token signed with JWT_SECRET."""
    secret = "test-super-secret-jwt-key-minimum-32-chars-long"
    now = int(time.time())
    payload = {
        "sub": "user_hs256_legacy_uuid",
        "aud": "authenticated",
        "iss": "https://zkpunneykkcegvfibcrm.supabase.co/auth/v1",
        "iat": now,
        "exp": now + 3600,
        "email": "legacy@example.com",
        "role": "patient",
    }
    token = jwt.encode(payload, secret, algorithm="HS256")

    verified = verify_token(token)
    assert verified["sub"] == "user_hs256_legacy_uuid"
    assert verified["email"] == "legacy@example.com"
    assert verified["role"] == "patient"


def test_hs256_wrong_secret_rejected():
    """Verify HS256 token signed with incorrect secret is rejected."""
    wrong_secret = "different-secret-key-123456789012345"
    token = jwt.encode(
        {
            "sub": "user_hs256",
            "aud": "authenticated",
            "iss": "https://zkpunneykkcegvfibcrm.supabase.co/auth/v1",
        },
        wrong_secret,
        algorithm="HS256",
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token(token)
    assert "Invalid or expired token" in str(exc_info.value)


def test_hs256_expired_token_rejected():
    """Verify expired HS256 token is rejected."""
    secret = "test-super-secret-jwt-key-minimum-32-chars-long"
    token = jwt.encode(
        {
            "sub": "user_expired_hs256",
            "aud": "authenticated",
            "iss": "https://zkpunneykkcegvfibcrm.supabase.co/auth/v1",
            "exp": int(time.time()) - 50,
        },
        secret,
        algorithm="HS256",
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token(token)
    assert "expired" in str(exc_info.value).lower()


# ==========================================
# 3. Security Boundary & Attack Defense Tests
# ==========================================

def test_reject_algorithm_none():
    """Verify critical security rule: algorithm 'none' is rejected."""
    # Attempt CVE-2015-9235 style attack
    token = jwt.encode({"sub": "admin", "aud": "authenticated"}, key="", algorithm="none")

    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token(token)
    assert "Unsupported signing algorithm" in str(exc_info.value)


def test_reject_unsupported_algorithm():
    """Verify algorithms not in whitelist (e.g., RS256) are rejected."""
    token = (
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwiYXVkIjoiYXV0aGVudGljYXRlZCJ9."
        "invalidsignature"
    )
    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token(token)
    assert "Unsupported signing algorithm 'RS256'" in str(exc_info.value)


def test_reject_missing_subject():
    """Verify token without 'sub' identifier is rejected."""
    secret = "test-super-secret-jwt-key-minimum-32-chars-long"
    token = jwt.encode(
        {"aud": "authenticated", "iss": "https://zkpunneykkcegvfibcrm.supabase.co/auth/v1"},
        secret,
        algorithm="HS256",
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token(token)
    assert "missing or invalid user identifier" in str(exc_info.value)


def test_reject_malformed_token():
    """Verify malformed token strings are safely rejected."""
    with pytest.raises(UnauthorizedError) as exc_info:
        verify_token("not-a-real-token")
    assert "Malformed" in str(exc_info.value) or "Invalid" in str(exc_info.value)


def test_reject_empty_token():
    """Verify empty token string is rejected."""
    with pytest.raises(UnauthorizedError):
        verify_token("")
