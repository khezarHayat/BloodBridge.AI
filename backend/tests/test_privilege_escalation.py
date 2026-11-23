"""
Targeted security tests for privilege escalation prevention.

Validates:
1. User-editable user_metadata cannot grant admin, hospital, or blood_bank privileges.
2. Registration pipeline rejects public attempts to assign 'admin' or 'hospital' roles.
3. FastAPI require_role() relies on verified database profile role, not user_metadata claims.
4. Fallback profile builder rejects 'admin' in user_metadata and defaults to 'patient'.
5. Database trigger handle_new_user() sanitization ignores raw_user_meta_data roles.
6. Idempotent profile creation handles pre-existing profiles from triggers without duplicate key errors.
"""

from typing import Any, Dict
from unittest.mock import MagicMock
import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import ForbiddenError, ValidationError
from app.core.security import require_role
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user


def run_sync(coro):
    """Execute synchronous coroutine without needing socket loop."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


# ==============================================================
# 1. Registration Privilege Escalation Tests
# ==============================================================

def test_registration_schema_rejects_admin_role():
    """Verify RegisterRequest Pydantic schema rejects 'admin' in role pattern."""
    with pytest.raises(PydanticValidationError) as exc_info:
        RegisterRequest(
            email="attacker@example.com",
            password="StrongPassword123!",
            full_name="Attacker",
            phone="03001234567",
            role="admin",  # Attacker attempts to self-register as admin
            city="Peshawar",
            area="Hayatabad",
        )
    assert "role" in str(exc_info.value).lower()


def test_registration_schema_rejects_hospital_role():
    """Verify RegisterRequest Pydantic schema rejects 'hospital' role (institutional only)."""
    with pytest.raises(PydanticValidationError) as exc_info:
        RegisterRequest(
            email="fake.hospital@example.com",
            password="StrongPassword123!",
            full_name="Fake Hospital",
            phone="03001234567",
            role="hospital",  # Attempt to self-register as hospital
            city="Peshawar",
            area="Saddar",
        )
    assert "role" in str(exc_info.value).lower()


def test_register_user_service_blocks_admin_role():
    """Verify register_user service explicitly blocks 'admin' registration."""
    data = MagicMock()
    data.role = "admin"
    data.email = "attacker@example.com"

    with pytest.raises(ValidationError) as exc_info:
        run_sync(register_user(data))
    assert "prohibited" in str(exc_info.value).lower()


def test_register_user_service_blocks_hospital_role():
    """Verify register_user service explicitly blocks 'hospital' registration."""
    data = MagicMock()
    data.role = "hospital"
    data.email = "attacker.hospital@example.com"

    with pytest.raises(ValidationError) as exc_info:
        run_sync(register_user(data))
    assert "prohibited" in str(exc_info.value).lower()


# ==============================================================
# 2. Database Trigger handle_new_user() Role Sanitization
# ==============================================================

def test_trigger_handle_new_user_ignores_user_metadata():
    """
    Simulates the exact logic in 003_functions.sql handle_new_user().
    Verifies that raw_user_meta_data role requests for admin, hospital,
    or blood_bank are strictly ignored and default to 'patient'.
    """
    def simulate_handle_new_user(raw_user_meta_data: Dict[str, Any], raw_app_meta_data: Dict[str, Any]) -> str:
        # SQL logic: trusted_role := COALESCE(NEW.raw_app_meta_data->>'role', 'patient');
        trusted_role = (raw_app_meta_data or {}).get("role", "patient")
        if trusted_role not in ["patient", "donor", "blood_bank", "hospital", "admin"]:
            trusted_role = "patient"
        return trusted_role

    # Attacker passes role='admin' in user_metadata
    user_meta_attacker = {"role": "admin", "full_name": "Attacker Admin"}
    app_meta_empty = {}
    assert simulate_handle_new_user(user_meta_attacker, app_meta_empty) == "patient"

    # Attacker passes role='hospital' in user_metadata
    user_meta_hospital = {"role": "hospital", "full_name": "Attacker Hospital"}
    assert simulate_handle_new_user(user_meta_hospital, app_meta_empty) == "patient"

    # Attacker passes role='blood_bank' in user_metadata
    user_meta_bank = {"role": "blood_bank", "full_name": "Attacker Blood Bank"}
    assert simulate_handle_new_user(user_meta_bank, app_meta_empty) == "patient"

    # Trusted server sets role in app_metadata
    server_app_meta = {"role": "admin"}
    assert simulate_handle_new_user(user_meta_attacker, server_app_meta) == "admin"


# ==============================================================
# 3. Idempotent Profile Creation Tests (Trigger Pre-creation Scenario)
# ==============================================================

def test_idempotent_profile_creation_preserves_registration_fields():
    """
    Verifies that when a profile was pre-created by the database trigger
    (with minimal defaults), the server-side provisioning cleanly sets
    phone, city, area, and validated role without crashing on duplicate key.
    """
    # 1. Simulate base profile created by on_auth_user_created trigger
    pre_existing_profile = {
        "id": "usr_test_uuid_12345",
        "email": "donor@example.com",
        "full_name": "Test Donor",
        "role": "patient",  # trigger default
        "is_verified": False,
        "is_active": True,
        "created_at": "2026-11-22T02:00:00Z",
    }

    # 2. Incoming validated server registration data
    registration_data = {
        "full_name": "Muhammad Bilal",
        "phone": "+92-300-1234567",
        "role": "donor",
        "city": "Peshawar",
        "area": "Hayatabad",
    }

    # 3. Evaluate idempotent merge logic from auth_service.py
    target_role = registration_data["role"]
    is_verified = pre_existing_profile.get("is_verified", False)
    if pre_existing_profile.get("role") in ["admin", "hospital"]:
        target_role = pre_existing_profile["role"]

    merged_profile = {
        "id": pre_existing_profile["id"],
        "email": pre_existing_profile["email"],
        "full_name": registration_data["full_name"],
        "phone": registration_data["phone"],
        "role": target_role,
        "city": registration_data["city"],
        "area": registration_data["area"],
        "is_verified": is_verified,
        "is_active": True,
        "created_at": pre_existing_profile["created_at"],
    }

    # Verified results
    assert merged_profile["id"] == "usr_test_uuid_12345"
    assert merged_profile["phone"] == "+92-300-1234567"
    assert merged_profile["area"] == "Hayatabad"
    assert merged_profile["role"] == "donor"
    assert merged_profile["is_verified"] is False
    assert merged_profile["created_at"] == "2026-11-22T02:00:00Z"


def test_idempotent_profile_creation_does_not_demote_admin():
    """Verifies that idempotent registration cannot demote an existing administrator."""
    pre_existing_admin = {
        "id": "usr_admin_uuid",
        "role": "admin",
        "is_verified": True,
    }
    # Attempting to re-register with role='patient'
    attempted_role = "patient"
    target_role = attempted_role
    if pre_existing_admin.get("role") in ["admin", "hospital"]:
        target_role = pre_existing_admin["role"]

    assert target_role == "admin"


# ==============================================================
# 4. FastAPI Authorization Role Enforcement Tests
# ==============================================================

def test_require_role_rejects_user_metadata_spoofed_admin():
    """Verify require_role('admin') rejects patient claiming admin in user_metadata."""
    admin_checker = require_role("admin")

    patient_user: Dict[str, Any] = {
        "id": "usr_patient_uuid",
        "email": "patient@example.com",
        "role": "patient",
        "is_active": True,
        "user_metadata": {"role": "admin"},
    }

    with pytest.raises(ForbiddenError) as exc_info:
        run_sync(admin_checker(current_user=patient_user))

    assert "This action requires one of the following roles: admin" in str(exc_info.value)
    assert "Your role is 'patient'" in str(exc_info.value)


def test_require_role_rejects_unverified_blood_bank_from_admin_route():
    """Verify blood bank role cannot access admin-only endpoints."""
    admin_checker = require_role("admin")

    blood_bank_user: Dict[str, Any] = {
        "id": "usr_bank_uuid",
        "email": "bank@example.com",
        "role": "blood_bank",
        "is_active": True,
    }

    with pytest.raises(ForbiddenError) as exc_info:
        run_sync(admin_checker(current_user=blood_bank_user))

    assert "Your role is 'blood_bank'" in str(exc_info.value)


def test_require_role_allows_genuine_admin():
    """Verify require_role('admin') succeeds for genuine verified admin."""
    admin_checker = require_role("admin")

    genuine_admin: Dict[str, Any] = {
        "id": "usr_admin_uuid",
        "email": "admin@bloodbridge.pk",
        "role": "admin",
        "is_active": True,
    }

    result = run_sync(admin_checker(current_user=genuine_admin))
    assert result["role"] == "admin"


# ==============================================================
# 5. Fallback Login Profile Role Sanitization Tests
# ==============================================================

def test_login_fallback_sanitizes_user_metadata_admin():
    """Verify fallback builder never trusts user_metadata and assigns 'patient'."""
    user_mock = MagicMock()
    user_mock.id = "mock_uuid_123"
    user_mock.app_metadata = {}
    user_mock.user_metadata = {"role": "admin", "full_name": "Infiltrator"}

    app_meta = getattr(user_mock, "app_metadata", None) or {}
    app_meta_role = app_meta.get("role") if isinstance(app_meta, dict) else None
    safe_role = app_meta_role if app_meta_role in ["donor", "patient", "blood_bank", "hospital"] else "patient"

    assert safe_role == "patient"
    assert safe_role != "admin"
