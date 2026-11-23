"""
Phase 2 Validation Tests: Patient Matched Donor View and Donor Invitation Tracking.

Tests:
1. Authorization: Only the request owner or admin can view invitations for a request; others get 403 Forbidden.
2. Privacy: Donor phone, email, and personal identifiers are strictly excluded, and donor names are masked.
3. Status Transitions: Accepting an invitation updates units_fulfilled and transitions request to 'donor_confirmed' or 'fulfilled'.
4. Notification Dispatch: Notifications are created for patients when donors accept or decline.
5. Audit History: Status transitions are logged to request_status_history.
"""

from collections import defaultdict
import anyio
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.core.exceptions import ForbiddenError, NotFoundError
from app.schemas.invitation import InvitationAction
from app.services.request_service import get_request_invitations, _mask_donor_name


def test_mask_donor_name():
    """Verify donor names are masked to protect personal privacy."""
    assert _mask_donor_name("Tariq Afridi") == "Tariq A."
    assert _mask_donor_name("Muhammad Ali Khan") == "Muhammad K."
    assert _mask_donor_name("Fatima") == "Fatima"
    assert _mask_donor_name(None) == "Volunteer Donor"
    assert _mask_donor_name("") == "Volunteer Donor"


def test_get_request_invitations_requester_allowed():
    """Requester should be able to view their request's invitations."""
    async def _test():
        mock_request = {
            "id": "req-123",
            "requester_id": "user-owner",
        }
        mock_invitations = [
            {
                "id": "inv-001",
                "request_id": "req-123",
                "donor_id": "donor-001",
                "status": "pending",
                "match_score": 92.5,
                "match_reasons": ["Exact match", "Close proximity"],
                "distance_km": 3.4,
                "invited_at": "2026-11-22T10:00:00Z",
                "responded_at": None,
                "donors": {
                    "blood_group": "B+",
                    "profiles": {
                        "full_name": "Tariq Afridi",
                        "area": "Hayatabad",
                    },
                },
            }
        ]

        with patch("app.services.request_service.get_blood_request", new=AsyncMock(return_value=mock_request)):
            with patch("app.services.request_service.get_supabase_admin") as mock_admin:
                mock_table = MagicMock()
                mock_select = MagicMock()
                mock_eq = MagicMock()
                mock_order = MagicMock()
                mock_res = MagicMock()
                mock_res.data = mock_invitations

                mock_admin.return_value.table.return_value = mock_table
                mock_table.select.return_value = mock_select
                mock_select.eq.return_value = mock_eq
                mock_eq.order.return_value = mock_order
                mock_order.execute.return_value = mock_res

                invs = await get_request_invitations("req-123", "user-owner", "patient")
                assert len(invs) == 1
                inv = invs[0]

                # Verify fields and privacy
                assert inv["status"] == "pending"
                assert inv["donor_name"] == "Tariq A."
                assert inv["donor_blood_group"] == "B+"
                assert inv["donor_area"] == "Hayatabad"
                assert inv["match_score"] == 92.5
                assert inv["distance_km"] == 3.4

                # Verify NO sensitive fields leaked
                assert "phone" not in inv
                assert "email" not in inv
                assert "address" not in inv
                assert "medical_conditions" not in inv

    anyio.run(_test)


def test_get_request_invitations_unauthorized_forbidden():
    """A patient who is not the requester should receive 403 Forbidden."""
    async def _test():
        mock_request = {
            "id": "req-123",
            "requester_id": "user-owner",
        }

        with patch("app.services.request_service.get_blood_request", new=AsyncMock(return_value=mock_request)):
            with pytest.raises(ForbiddenError, match="Not authorized"):
                await get_request_invitations("req-123", "different-user", "patient")

    anyio.run(_test)


def test_get_request_invitations_admin_allowed():
    """An admin should be allowed to view any request's invitations."""
    async def _test():
        mock_request = {
            "id": "req-123",
            "requester_id": "user-owner",
        }
        with patch("app.services.request_service.get_blood_request", new=AsyncMock(return_value=mock_request)):
            with patch("app.services.request_service.get_supabase_admin") as mock_admin:
                mock_table = MagicMock()
                mock_select = MagicMock()
                mock_eq = MagicMock()
                mock_order = MagicMock()
                mock_res = MagicMock()
                mock_res.data = []

                mock_admin.return_value.table.return_value = mock_table
                mock_table.select.return_value = mock_select
                mock_select.eq.return_value = mock_eq
                mock_eq.order.return_value = mock_order
                mock_order.execute.return_value = mock_res

                invs = await get_request_invitations("req-123", "admin-user", "admin")
                assert invs == []

    anyio.run(_test)


def test_donor_accept_invitation_updates_status_and_notifies():
    """Accepting an invitation increments units, updates status to donor_confirmed, and notifies patient."""
    async def _test():
        from app.services.donor_service import respond_to_invitation

        invitation_id = "inv-001"
        donor_user_id = "donor-user-1"
        donor_id = "donor-id-1"
        request_id = "req-001"

        action = InvitationAction(status="accepted", response_notes="I will be there in 1 hour")

        mock_donor_res = MagicMock(data={"id": donor_id, "total_donations": 2})
        mock_inv_res = MagicMock(data={
            "id": invitation_id,
            "donor_id": donor_id,
            "request_id": request_id,
            "status": "pending",
        })
        mock_req_res = MagicMock(data={
            "id": request_id,
            "units_needed": 2,
            "units_fulfilled": 0,
            "status": "matching",
            "requester_id": "patient-user-1",
        })

        with patch("app.services.donor_service.get_supabase_admin") as mock_admin:
            tables = defaultdict(MagicMock)
            mock_admin.return_value.table.side_effect = lambda name: tables[name]

            # Setup donors lookup
            tables["donors"].select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_donor_res

            # Setup invitations lookup
            tables["donor_invitations"].select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_inv_res
            tables["donor_invitations"].update.return_value.eq.return_value.execute.return_value = MagicMock(
                data=[{"id": invitation_id, "status": "accepted"}]
            )

            # Setup blood_requests lookup
            tables["blood_requests"].select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_req_res

            # Setup profile lookup for notification
            tables["profiles"].select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                data={"full_name": "Hamza Shinwari"}
            )

            result = await respond_to_invitation(invitation_id, donor_user_id, action)
            assert result["status"] == "accepted"

            # Verify blood request was updated to donor_confirmed (1 unit out of 2)
            tables["blood_requests"].update.assert_called()
            update_args = tables["blood_requests"].update.call_args[0][0]
            assert update_args["units_fulfilled"] == 1
            assert update_args["status"] == "donor_confirmed"

            # Verify notification was dispatched to requester
            tables["notifications"].insert.assert_called()
            notification_payload = tables["notifications"].insert.call_args[0][0]
            assert notification_payload["user_id"] == "patient-user-1"
            assert notification_payload["type"] == "request_update"
            assert "accepted" in notification_payload["title"].lower()
            assert "Hamza S." in notification_payload["message"]

            # Verify status history was recorded
            tables["request_status_history"].insert.assert_called()
            history_payload = tables["request_status_history"].insert.call_args[0][0]
            assert history_payload["old_status"] == "matching"
            assert history_payload["new_status"] == "donor_confirmed"

    anyio.run(_test)


def test_donor_decline_invitation_notifies_patient():
    """Declining an invitation notifies the patient of the update."""
    async def _test():
        from app.services.donor_service import respond_to_invitation

        invitation_id = "inv-002"
        donor_user_id = "donor-user-2"
        donor_id = "donor-id-2"
        request_id = "req-002"

        action = InvitationAction(status="declined", response_notes="Currently unavailable")

        mock_donor_res = MagicMock(data={"id": donor_id, "total_donations": 1})
        mock_inv_res = MagicMock(data={
            "id": invitation_id,
            "donor_id": donor_id,
            "request_id": request_id,
            "status": "pending",
        })
        mock_req_res = MagicMock(data={
            "id": request_id,
            "units_needed": 1,
            "units_fulfilled": 0,
            "status": "matching",
            "requester_id": "patient-user-2",
        })

        with patch("app.services.donor_service.get_supabase_admin") as mock_admin:
            tables = defaultdict(MagicMock)
            mock_admin.return_value.table.side_effect = lambda name: tables[name]

            # Setup donors lookup
            tables["donors"].select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_donor_res

            # Setup invitations lookup
            tables["donor_invitations"].select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_inv_res
            tables["donor_invitations"].update.return_value.eq.return_value.execute.return_value = MagicMock(
                data=[{"id": invitation_id, "status": "declined"}]
            )

            # Setup blood_requests lookup
            tables["blood_requests"].select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_req_res

            # Setup invitation status check
            tables["donor_invitations"].select.return_value.eq.return_value.execute.return_value = MagicMock(
                data=[{"status": "declined"}]
            )

            result = await respond_to_invitation(invitation_id, donor_user_id, action)
            assert result["status"] == "declined"

            # Verify notification was sent to requester
            tables["notifications"].insert.assert_called()
            notif_args = tables["notifications"].insert.call_args[0][0]
            assert notif_args["user_id"] == "patient-user-2"
            assert notif_args["type"] == "request_update"
            assert "unable to fulfill" in notif_args["message"] or "unavailable" in notif_args["message"]

    anyio.run(_test)
