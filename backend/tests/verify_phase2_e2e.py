"""
BloodBridge AI — Phase 2 Live End-to-End Workflow Verification Script.

Tests all 10 live operational workflows:
1. Patient login via FastAPI / Supabase Auth.
2. Emergency blood request creation with geolocation.
3. Patient view of matched donor invitations.
4. Donor login and invitation visibility.
5. Donor accepts invitation.
6. Patient dashboard verification of 'accepted' status and request progression.
7. Second donor decline workflow and verification of 'declined' status.
8. Patient notification reception for both acceptance and decline.
9. Cross-patient authorization isolation (403 Forbidden for other patients).
10. Privacy audit: strict absence of phone numbers, emails, addresses, and full names.
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import get_settings


async def run_e2e_verification():
    print("=" * 80)
    print("  BLOODBRIDGE AI — PHASE 2 LIVE END-TO-END VERIFICATION")
    print("=" * 80)

    results = {}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        # -------------------------------------------------------------
        # STEP 1: Log in as patient1
        # -------------------------------------------------------------
        print("\n[Step 1] Logging in as patient1 (Nasir Khan)...")
        login_res = await client.post(
            "/api/auth/login",
            json={"email": "patient1@bloodbridge.demo", "password": "DemoPassword123!"},
        )
        assert login_res.status_code == 200, f"Patient login failed: {login_res.text}"
        patient_token = login_res.json()["access_token"]
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        print(f"  -> SUCCESS: Patient authenticated (Token received: {patient_token[:15]}...)")
        results["step_1_patient_login"] = "PASSED"

        # -------------------------------------------------------------
        # STEP 2: Create emergency blood request
        # -------------------------------------------------------------
        print("\n[Step 2] Creating emergency blood request (A+ urgent at HMC, Hayatabad)...")
        req_payload = {
            "patient_name": "Hamza Shinwari (E2E Test Patient)",
            "blood_group": "A+",
            "units_needed": 2,
            "hospital_name": "Hayatabad Medical Complex (HMC)",
            "hospital_address": "Phase 4, Hayatabad, Peshawar",
            "city": "Peshawar",
            "area": "Hayatabad",
            "latitude": 34.0017,
            "longitude": 71.4448,
            "emergency_level": "urgent",
            "contact_name": "Nasir Khan (Attendant)",
            "contact_phone": "03001234567",
            "additional_notes": "Emergency surgery transfusion needed immediately",
        }
        create_res = await client.post("/api/blood-requests/", json=req_payload, headers=patient_headers)
        assert create_res.status_code == 201, f"Create request failed: {create_res.text}"
        req_data = create_res.json()
        request_id = req_data["id"]
        request_number = req_data["request_number"]
        print(f"  -> SUCCESS: Request created: ID={request_id}, Number={request_number}")
        print(f"  -> Matched donors dispatched by AI engine: {req_data.get('matched_donors', 0)}")
        results["step_2_create_request"] = "PASSED"

        # -------------------------------------------------------------
        # STEP 3: Verify matched donor invitations appear in patient view
        # -------------------------------------------------------------
        print("\n[Step 3] Fetching matched donor invitations from patient view...")
        invs_res = await client.get(f"/api/blood-requests/{request_id}/invitations", headers=patient_headers)
        assert invs_res.status_code == 200, f"Get invitations failed: {invs_res.text}"
        invitations = invs_res.json()
        print(f"  -> SUCCESS: Retrieved {len(invitations)} candidate invitations for request")
        assert len(invitations) >= 2, f"Expected at least 2 invitations for A+ in Peshawar, got {len(invitations)}"

        inv_1 = invitations[0]
        inv_2 = invitations[1]
        print(f"  Candidate 1: Status={inv_1['status']}, Masked Name={inv_1.get('donor_name')}, Group={inv_1.get('donor_blood_group')}, Dist={inv_1.get('distance_km')} km, Score={inv_1.get('match_score')}%")
        print(f"  Candidate 2: Status={inv_2['status']}, Masked Name={inv_2.get('donor_name')}, Group={inv_2.get('donor_blood_group')}, Dist={inv_2.get('distance_km')} km, Score={inv_2.get('match_score')}%")
        assert inv_1["status"] == "pending", f"Initial status should be pending, got {inv_1['status']}"
        assert inv_2["status"] == "pending", f"Initial status should be pending, got {inv_2['status']}"
        results["step_3_invitations_visible"] = "PASSED"

        # -------------------------------------------------------------
        # STEP 4: Log in as Candidate 1 and verify invitation is visible
        # -------------------------------------------------------------
        from app.core.supabase_client import get_supabase_admin
        supabase = get_supabase_admin()
        c1_donor_id = inv_1["donor_id"]
        c1_inv_id = inv_1["id"]
        d1_rec = supabase.table("donors").select("user_id, profiles:user_id(email, full_name)").eq("id", c1_donor_id).single().execute()
        d1_email = d1_rec.data["profiles"]["email"]
        d1_name = d1_rec.data["profiles"]["full_name"]
        print(f"\n[Step 4] Logging in as Candidate 1 ({d1_email} - {d1_name})...")

        donor1_login = await client.post(
            "/api/auth/login",
            json={"email": d1_email, "password": "DemoPassword123!"},
        )
        assert donor1_login.status_code == 200, f"Donor 1 login failed: {donor1_login.text}"
        donor1_token = donor1_login.json()["access_token"]
        donor1_headers = {"Authorization": f"Bearer {donor1_token}"}

        # Check donor 1 invitations
        donor1_invs_res = await client.get("/api/donors/me/invitations", headers=donor1_headers)
        assert donor1_invs_res.status_code == 200, f"Get donor invitations failed: {donor1_invs_res.text}"
        donor1_invs = donor1_invs_res.json().get("invitations", [])
        
        # Find matching invitation for this request
        target_inv1 = next((i for i in donor1_invs if i["request_id"] == request_id), None)
        assert target_inv1 is not None, f"Invitation for request {request_id} not found in Donor 1's dashboard"
        print(f"  -> SUCCESS: Invitation {target_inv1['id']} visible in Candidate 1 ({d1_name}) dashboard with status '{target_inv1['status']}'")
        results["step_4_donor_invitation_visible"] = "PASSED"

        # -------------------------------------------------------------
        # STEP 5: Donor 1 accepts invitation
        # -------------------------------------------------------------
        print("\n[Step 5] Donor 1 accepting invitation...")
        accept_res = await client.put(
            f"/api/donors/invitations/{target_inv1['id']}",
            json={"status": "accepted", "response_notes": "I am nearby and can arrive within 30 minutes."},
            headers=donor1_headers,
        )
        assert accept_res.status_code == 200, f"Accept invitation failed: {accept_res.text}"
        accept_data = accept_res.json()
        assert accept_data["status"] == "accepted", f"Expected accepted, got {accept_data['status']}"
        print(f"  -> SUCCESS: Donor 1 accepted invitation {target_inv1['id']}")
        results["step_5_donor_accept"] = "PASSED"

        # -------------------------------------------------------------
        # STEP 6: Verify patient dashboard displays 'Accepted'
        # -------------------------------------------------------------
        print("\n[Step 6] Verifying patient dashboard reflects 'accepted' status...")
        invs_after_accept_res = await client.get(f"/api/blood-requests/{request_id}/invitations", headers=patient_headers)
        assert invs_after_accept_res.status_code == 200
        invs_after_accept = invs_after_accept_res.json()
        accepted_inv = next((i for i in invs_after_accept if i["id"] == target_inv1["id"]), None)
        assert accepted_inv is not None
        assert accepted_inv["status"] == "accepted", f"Expected invitation status 'accepted', got '{accepted_inv['status']}'"
        print(f"  -> SUCCESS: Patient view shows Candidate {accepted_inv['donor_name']} as 'ACCEPTED' (Responded at: {accepted_inv['responded_at']})")

        # Check blood request status
        req_check = await client.get(f"/api/blood-requests/{request_id}", headers=patient_headers)
        assert req_check.status_code == 200
        req_status = req_check.json()
        print(f"  -> Blood Request Status: '{req_status['status']}', Units Fulfilled: {req_status['units_fulfilled']} / {req_status['units_needed']}")
        assert req_status["status"] == "donor_confirmed", f"Expected 'donor_confirmed', got '{req_status['status']}'"
        assert req_status["units_fulfilled"] == 1, f"Expected 1 unit fulfilled, got {req_status['units_fulfilled']}"
        results["step_6_patient_sees_accepted"] = "PASSED"

        # -------------------------------------------------------------
        # STEP 7: Second donor tests 'Declined'
        # -------------------------------------------------------------
        print("\n[Step 7] Testing decline workflow with Candidate 2...")
        # Dynamically lookup candidate 2's user email
        c2_donor_id = inv_2["donor_id"]
        c2_inv_id = inv_2["id"]
        from app.core.supabase_client import get_supabase_admin
        supabase = get_supabase_admin()
        d2_rec = supabase.table("donors").select("user_id, profiles:user_id(email)").eq("id", c2_donor_id).single().execute()
        d2_email = d2_rec.data["profiles"]["email"]
        print(f"  Candidate 2 Invitation ID: {c2_inv_id}, Email: {d2_email}")

        donor2_login = await client.post(
            "/api/auth/login",
            json={"email": d2_email, "password": "DemoPassword123!"},
        )
        assert donor2_login.status_code == 200
        donor2_token = donor2_login.json()["access_token"]
        donor2_headers = {"Authorization": f"Bearer {donor2_token}"}

        # Check donor 2 invitations
        donor2_invs_res = await client.get("/api/donors/me/invitations", headers=donor2_headers)
        donor2_invs = donor2_invs_res.json().get("invitations", [])
        target_inv2 = next((i for i in donor2_invs if i["request_id"] == request_id), None)
        assert target_inv2 is not None, f"Invitation for request {request_id} not found in Donor 2's dashboard"

        # Decline
        decline_res = await client.put(
            f"/api/donors/invitations/{target_inv2['id']}",
            json={"status": "declined", "response_notes": "Unavailable due to travel."},
            headers=donor2_headers,
        )
        assert decline_res.status_code == 200
        assert decline_res.json()["status"] == "declined"
        print(f"  -> SUCCESS: Donor 2 declined invitation {target_inv2['id']}")

        # Verify patient view shows candidate 2 as 'declined'
        invs_after_decline = (await client.get(f"/api/blood-requests/{request_id}/invitations", headers=patient_headers)).json()
        declined_inv = next((i for i in invs_after_decline if i["id"] == target_inv2["id"]), None)
        assert declined_inv is not None
        assert declined_inv["status"] == "declined", f"Expected declined, got {declined_inv['status']}"
        print(f"  -> SUCCESS: Patient view shows Candidate {declined_inv['donor_name']} as 'DECLINED'")
        results["step_7_second_donor_declined"] = "PASSED"

        # -------------------------------------------------------------
        # STEP 8: Verify patient notifications
        # -------------------------------------------------------------
        print("\n[Step 8] Checking patient notifications...")
        notifs_res = await client.get("/api/notifications/", headers=patient_headers)
        assert notifs_res.status_code == 200
        notifs_data = notifs_res.json()
        notifs = notifs_data.get("notifications", [])
        print(f"  -> Retrieved {len(notifs)} notifications for patient")

        # Find acceptance notification
        accept_notif = next((n for n in notifs if "accept" in n["title"].lower() and n.get("reference_id") == request_id), None)
        assert accept_notif is not None, "Acceptance notification not found for patient"
        print(f"  -> Found Acceptance Alert: '{accept_notif['title']}' — '{accept_notif['message']}'")

        # Find decline notification
        decline_notif = next((n for n in notifs if "invitation update" in n["title"].lower() and n.get("reference_id") == request_id), None)
        assert decline_notif is not None, "Decline update notification not found for patient"
        print(f"  -> Found Decline Alert: '{decline_notif['title']}' — '{decline_notif['message']}'")
        results["step_8_patient_notifications"] = "PASSED"

        # -------------------------------------------------------------
        # STEP 9: Cross-patient authorization check (403 Forbidden)
        # -------------------------------------------------------------
        print("\n[Step 9] Testing cross-patient authorization isolation...")
        patient2_login = await client.post(
            "/api/auth/login",
            json={"email": "patient2@bloodbridge.demo", "password": "DemoPassword123!"},
        )
        assert patient2_login.status_code == 200
        patient2_token = patient2_login.json()["access_token"]
        patient2_headers = {"Authorization": f"Bearer {patient2_token}"}

        # Patient 2 attempts to access Patient 1's request invitations
        unauth_res = await client.get(f"/api/blood-requests/{request_id}/invitations", headers=patient2_headers)
        print(f"  -> Patient 2 access attempt response: HTTP {unauth_res.status_code}")
        assert unauth_res.status_code == 403, f"Expected 403 Forbidden, got {unauth_res.status_code}"
        print("  -> SUCCESS: Unauthorized patient strictly blocked with HTTP 403 Forbidden")
        results["step_9_cross_patient_authorization"] = "PASSED"

        # -------------------------------------------------------------
        # STEP 10: Donor privacy audit
        # -------------------------------------------------------------
        print("\n[Step 10] Auditing donor privacy in patient API response...")
        for inv in invs_after_decline:
            # Check top-level keys
            assert "phone" not in inv, "LEAK: 'phone' found in invitation payload"
            assert "email" not in inv, "LEAK: 'email' found in invitation payload"
            assert "medical_conditions" not in inv, "LEAK: 'medical_conditions' found in invitation payload"
            assert "address" not in inv, "LEAK: 'address' found in invitation payload"

            # Check nested donors & profiles object
            donors_obj = inv.get("donors", {})
            profiles_obj = donors_obj.get("profiles", {})
            assert "phone" not in profiles_obj, "LEAK: 'phone' found in profiles payload"
            assert "email" not in profiles_obj, "LEAK: 'email' found in profiles payload"
            assert "address" not in profiles_obj, "LEAK: 'address' found in profiles payload"

            # Check that donor name is masked (contains initials, not full surname)
            name = inv.get("donor_name", "")
            print(f"  Audited donor: Name='{name}', Area='{inv.get('donor_area')}', Group='{inv.get('donor_blood_group')}'")
            # Should end with a period like "Muhammad B." or be a single name
            assert name.endswith(".") or len(name.split()) == 1, f"Expected masked name, got '{name}'"

        print("  -> SUCCESS: All donor privacy rules verified. Zero personal contact leaks.")
        results["step_10_donor_privacy"] = "PASSED"

    print("\n" + "=" * 80)
    print("  E2E SUMMARY:")
    for k, v in results.items():
        print(f"    {k}: {v}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_e2e_verification())
