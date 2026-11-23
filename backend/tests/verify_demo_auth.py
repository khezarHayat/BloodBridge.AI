"""
BloodBridge: Live Demo Auth & /api/auth/me Verification Script

Tests real authentication against Supabase Auth for all 4 demo user roles:
1. Admin (admin1@bloodbridge.demo)
2. Donor (donor01@bloodbridge.demo)
3. Blood Bank (lrh.bloodbank@bloodbridge.demo)
4. Patient (patient1@bloodbridge.demo)

For each user:
- Performs real sign_in_with_password against Supabase Auth API
- Validates the returned Supabase JWT token using backend token verification
- Confirms the trusted role matches expectations
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from supabase import create_client
from app.core.config import get_settings
from app.core.security import verify_token

DEMO_USERS = [
    {
        "role": "admin",
        "email": "admin1@bloodbridge.demo",
        "password": "DemoPassword123!",
        "expected_name": "Dr. Ahmad Khan",
    },
    {
        "role": "donor",
        "email": "donor01@bloodbridge.demo",
        "password": "DemoPassword123!",
        "expected_name": "Muhammad Bilal",
    },
    {
        "role": "blood_bank",
        "email": "lrh.bloodbank@bloodbridge.demo",
        "password": "DemoPassword123!",
        "expected_name": "Lady Reading Hospital Blood Bank",
    },
    {
        "role": "patient",
        "email": "patient1@bloodbridge.demo",
        "password": "DemoPassword123!",
        "expected_name": "Nasir Khan",
    },
]


def test_auth():
    settings = get_settings()
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    admin_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

    print("=" * 70)
    print("  BLOODBRIDGE — SUPABASE AUTH DEMO LOGIN & JWT VERIFICATION")
    print("=" * 70)

    results = []

    for account in DEMO_USERS:
        role = account["role"]
        email = account["email"]
        password = account["password"]
        print(f"\n[TESTING] Role: {role.upper()} | Email: {email}")

        try:
            # 1. Supabase Auth sign-in
            auth_res = client.auth.sign_in_with_password({"email": email, "password": password})
            session = auth_res.session
            user = auth_res.user

            if not session or not session.access_token:
                print(f"  [FAIL] No access token returned for {email}")
                results.append((role, False, "No access token"))
                continue

            token = session.access_token
            print(f"  [PASS] Supabase sign_in_with_password succeeded!")
            print(f"         User ID: {user.id}")

            # 2. Inspect token claims & verify token
            user_data = verify_token(token)
            verified_role = user_data.role
            verified_id = user_data.id
            print(f"  [PASS] JWT verified by backend security: role='{verified_role}', sub='{verified_id}'")

            # 3. Verify public.profiles record
            profile_res = (
                admin_client.table("profiles")
                .select("id, email, full_name, role, is_active, is_verified")
                .eq("id", user.id)
                .single()
                .execute()
            )
            profile = profile_res.data
            print(f"  [PASS] Profile lookup: name='{profile['full_name']}', role='{profile['role']}', active={profile['is_active']}")

            assert profile["role"] == role, f"Role mismatch: expected {role}, got {profile['role']}"
            results.append((role, True, f"Verified as {role}"))

        except Exception as e:
            print(f"  [FAIL] Error for {role} ({email}): {type(e).__name__}: {e}")
            results.append((role, False, str(e)))

    print("\n" + "=" * 70)
    print("  SUMMARY OF DEMO AUTH CHECKS")
    print("=" * 70)
    all_passed = True
    for role, passed, msg in results:
        status = "PASSED" if passed else "FAILED"
        if not passed:
            all_passed = False
        print(f"  [{status}] {role.upper():<12}: {msg}")
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    success = test_auth()
    sys.exit(0 if success else 1)
