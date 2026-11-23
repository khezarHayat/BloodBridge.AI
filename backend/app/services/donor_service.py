"""
Donor service.

Handles donor profile creation, updates, availability management,
invitation handling, and donor listing with filtering.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.core.supabase_client import get_supabase_admin
from app.schemas.donor import DonorCreate, DonorUpdate
from app.schemas.invitation import InvitationAction
from app.utils.pagination import get_count_from_response, paginate_response

logger = get_logger(__name__)


async def create_donor(user_id: str, data: DonorCreate) -> Dict[str, Any]:
    """
    Create a donor profile for a user.

    If a donor record already exists for this user (created during registration),
    it will be updated with the provided data. Otherwise, a new record is created.

    Args:
        user_id: The authenticated user's ID.
        data: Donor creation data.

    Returns:
        The created/updated donor record.

    Raises:
        ConflictError: If a fully configured donor profile already exists.
    """
    supabase = get_supabase_admin()
    now = datetime.now(timezone.utc).isoformat()

    # Check for existing donor record
    existing = (
        supabase.table("donors")
        .select("*")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )

    donor_data = {
        "user_id": user_id,
        "blood_group": data.blood_group,
        "date_of_birth": data.date_of_birth.isoformat() if data.date_of_birth else None,
        "gender": data.gender,
        "weight": data.weight,
        "last_donation_date": data.last_donation_date.isoformat() if data.last_donation_date else None,
        "consent_notifications": data.consent_notifications,
        "medical_conditions": data.medical_conditions,
        "is_available": True,
        "total_donations": 0,
        "availability_radius_km": 25.0,
        "updated_at": now,
    }

    if existing and existing.data:
        # Update existing record
        result = (
            supabase.table("donors")
            .update(donor_data)
            .eq("user_id", user_id)
            .execute()
        )
        logger.info("donor_profile_updated", user_id=user_id)
    else:
        donor_data["created_at"] = now
        result = supabase.table("donors").insert(donor_data).execute()
        logger.info("donor_profile_created", user_id=user_id)

    if not result or not result.data:
        raise ValidationError("Failed to create donor profile")

    return result.data[0]


async def update_donor(donor_id: str, user_id: str, data: DonorUpdate) -> Dict[str, Any]:
    """
    Update a donor's profile.

    Only the donor themselves can update their profile.

    Args:
        donor_id: The donor record ID.
        user_id: The authenticated user's ID (for ownership check).
        data: Donor update data.

    Returns:
        Updated donor record.

    Raises:
        NotFoundError: If donor record doesn't exist.
        ForbiddenError: If user is not the donor.
    """
    supabase = get_supabase_admin()

    # Verify ownership
    existing = (
        supabase.table("donors")
        .select("*")
        .eq("id", donor_id)
        .maybe_single()
        .execute()
    )

    if not existing or not existing.data:
        raise NotFoundError("Donor", donor_id)

    if existing.data.get("user_id") != user_id:
        raise ForbiddenError("You can only update your own donor profile")

    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        return existing.data

    # Convert date fields
    if "last_donation_date" in update_data and update_data["last_donation_date"]:
        update_data["last_donation_date"] = update_data["last_donation_date"].isoformat()

    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    result = (
        supabase.table("donors")
        .update(update_data)
        .eq("id", donor_id)
        .execute()
    )

    if not result or not result.data:
        raise NotFoundError("Donor", donor_id)

    logger.info("donor_updated", donor_id=donor_id, updated_fields=list(update_data.keys()))
    return result.data[0]


async def toggle_availability(donor_id: str, user_id: str, is_available: bool) -> Dict[str, Any]:
    """
    Toggle a donor's availability status.

    Args:
        donor_id: The donor record ID.
        user_id: The authenticated user's ID.
        is_available: New availability status.

    Returns:
        Updated donor record.
    """
    supabase = get_supabase_admin()

    # Verify ownership
    existing = (
        supabase.table("donors")
        .select("*")
        .eq("id", donor_id)
        .maybe_single()
        .execute()
    )

    if not existing or not existing.data:
        raise NotFoundError("Donor", donor_id)

    if existing.data.get("user_id") != user_id:
        raise ForbiddenError("You can only update your own availability")

    result = (
        supabase.table("donors")
        .update(
            {
                "is_available": is_available,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        .eq("id", donor_id)
        .execute()
    )

    if not result or not result.data:
        raise NotFoundError("Donor", donor_id)

    logger.info("donor_availability_toggled", donor_id=donor_id, is_available=is_available)
    return result.data[0]


async def get_donor(donor_id: str) -> Dict[str, Any]:
    """
    Get a single donor's details including profile information.

    Args:
        donor_id: The donor record ID.

    Returns:
        Donor record with profile data.
    """
    supabase = get_supabase_admin()

    result = (
        supabase.table("donors")
        .select("*, profiles(full_name, city, area, phone, is_verified, avatar_url)")
        .eq("id", donor_id)
        .maybe_single()
        .execute()
    )

    if not result or not result.data:
        raise NotFoundError("Donor", donor_id)

    donor = result.data
    profile = donor.pop("profiles", {}) or {}
    if isinstance(profile, list):
        profile = profile[0] if profile else {}

    donor["full_name"] = profile.get("full_name", "")
    donor["city"] = profile.get("city", "")
    donor["area"] = profile.get("area", donor.get("area", ""))
    donor["is_verified"] = profile.get("is_verified", False)

    return donor


async def list_donors(
    blood_group: Optional[str] = None,
    area: Optional[str] = None,
    city: Optional[str] = None,
    is_available: Optional[bool] = None,
    page: int = 1,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    List donors with optional filters and pagination.

    Args:
        blood_group: Filter by blood group.
        area: Filter by area.
        city: Filter by city.
        is_available: Filter by availability.
        page: Page number (1-indexed).
        limit: Items per page.

    Returns:
        Dictionary with donors list and pagination metadata.
    """
    supabase = get_supabase_admin()
    offset = (page - 1) * limit

    # Build query
    query = supabase.table("donors").select(
        "*, profiles(full_name, city, area, is_verified)",
        count="exact",
    )

    if blood_group:
        query = query.eq("blood_group", blood_group)
    if is_available is not None:
        query = query.eq("is_available", is_available)
    if city:
        query = query.eq("profiles.city", city)

    query = query.range(offset, offset + limit - 1)
    query = query.order("created_at", desc=True)

    result = query.execute()
    total = get_count_from_response(result)
    donors_data = result.data or []

    # Flatten profile data into donor records
    donors = []
    for donor in donors_data:
        profile = donor.pop("profiles", {}) or {}
        if isinstance(profile, list):
            profile = profile[0] if profile else {}

        donor["full_name"] = profile.get("full_name", "")
        donor["city"] = profile.get("city", "")
        donor["area"] = profile.get("area", donor.get("area", ""))
        donor["is_verified"] = profile.get("is_verified", False)

        # Apply area filter post-query if needed
        if area and donor.get("area", "").lower() != area.lower():
            total -= 1
            continue

        donors.append(donor)

    pagination = paginate_response(donors, total, page, limit)

    return {
        "donors": donors,
        **pagination,
    }


async def get_donor_invitations(user_id: str) -> Dict[str, Any]:
    """
    Get all invitations for a donor (by their user_id).

    Args:
        user_id: The authenticated donor's user ID.

    Returns:
        Dictionary with invitations list and total count.
    """
    supabase = get_supabase_admin()

    # First, get the donor record for this user
    donor_result = (
        supabase.table("donors")
        .select("id")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )

    if not donor_result or not donor_result.data:
        raise NotFoundError("Donor profile")

    donor_id = donor_result.data["id"]

    # Fetch invitations with request details
    result = (
        supabase.table("donor_invitations")
        .select(
            "*, blood_requests(patient_name, blood_group, hospital_name, "
            "emergency_level, city, area, units_needed, required_by, status)"
        )
        .eq("donor_id", donor_id)
        .order("invited_at", desc=True)
        .execute()
    )

    invitations_data = result.data or []
    invitations = []

    for inv in invitations_data:
        request_data = inv.pop("blood_requests", {}) or {}
        if isinstance(request_data, list):
            request_data = request_data[0] if request_data else {}

        inv["patient_name"] = request_data.get("patient_name")
        inv["blood_group"] = request_data.get("blood_group")
        inv["hospital_name"] = request_data.get("hospital_name")
        inv["emergency_level"] = request_data.get("emergency_level")
        invitations.append(inv)

    return {
        "invitations": invitations,
        "total": len(invitations),
    }


async def respond_to_invitation(
    invitation_id: str,
    user_id: str,
    action: InvitationAction,
) -> Dict[str, Any]:
    """
    Accept or decline a donor invitation.

    When accepting, updates the blood request's units_fulfilled count
    and potentially its status.

    Args:
        invitation_id: The invitation record ID.
        user_id: The authenticated donor's user ID.
        action: Accept or decline action.

    Returns:
        Updated invitation record.

    Raises:
        NotFoundError: If invitation doesn't exist.
        ForbiddenError: If user is not the invited donor.
        ValidationError: If invitation is not in pending status.
    """
    supabase = get_supabase_admin()

    # Get the donor record
    donor_result = (
        supabase.table("donors")
        .select("id")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )

    if not donor_result or not donor_result.data:
        raise NotFoundError("Donor profile")

    donor_id = donor_result.data["id"]

    # Fetch the invitation
    inv_result = (
        supabase.table("donor_invitations")
        .select("*")
        .eq("id", invitation_id)
        .maybe_single()
        .execute()
    )

    if not inv_result or not inv_result.data:
        raise NotFoundError("Invitation", invitation_id)

    invitation = inv_result.data

    if invitation.get("donor_id") != donor_id:
        raise ForbiddenError("This invitation is not for you")

    if invitation.get("status") != "pending":
        raise ValidationError(
            f"Cannot respond to invitation with status '{invitation.get('status')}'. "
            f"Only pending invitations can be responded to."
        )

    now = datetime.now(timezone.utc).isoformat()

    # Update invitation status
    update_data = {
        "status": action.status,
        "responded_at": now,
        "response_notes": action.response_notes,
    }

    result = (
        supabase.table("donor_invitations")
        .update(update_data)
        .eq("id", invitation_id)
        .execute()
    )

    if not result or not result.data:
        raise ValidationError("Failed to update invitation")

    # If accepted, update the blood request and notify requester
    request_id = invitation.get("request_id")
    if action.status == "accepted":
        if request_id:
            request_result = (
                supabase.table("blood_requests")
                .select("units_needed, units_fulfilled, status, requester_id")
                .eq("id", request_id)
                .maybe_single()
                .execute()
            )

            if request_result and request_result.data:
                req = request_result.data
                old_status = req.get("status")
                new_fulfilled = (req.get("units_fulfilled") or 0) + 1
                units_needed = req.get("units_needed", 1)

                new_status = "donor_confirmed"
                if new_fulfilled >= units_needed:
                    new_status = "fulfilled"

                req_update_payload: Dict[str, Any] = {
                    "units_fulfilled": new_fulfilled,
                    "status": new_status,
                    "updated_at": now,
                }
                if new_status == "fulfilled":
                    req_update_payload["fulfilled_at"] = now

                supabase.table("blood_requests").update(req_update_payload).eq("id", request_id).execute()

                # Record status history audit
                try:
                    supabase.table("request_status_history").insert({
                        "request_id": request_id,
                        "old_status": old_status,
                        "new_status": new_status,
                        "changed_by": user_id,
                        "notes": f"Donor accepted invitation. Units fulfilled: {new_fulfilled}/{units_needed}",
                        "created_at": now,
                    }).execute()
                except Exception as e:
                    logger.warning("status_history_accepted_failed", error=str(e))

                # Notify requester with privacy-protected donor identity
                try:
                    donor_name_result = (
                        supabase.table("profiles")
                        .select("full_name")
                        .eq("id", user_id)
                        .maybe_single()
                        .execute()
                    )
                    raw_donor_name = donor_name_result.data.get("full_name") if donor_name_result and donor_name_result.data else None
                    if raw_donor_name:
                        parts = raw_donor_name.strip().split()
                        donor_name = f"{parts[0]} {parts[-1][0]}." if len(parts) > 1 else parts[0]
                    else:
                        donor_name = "A matched donor"

                    requester_id = req.get("requester_id")
                    if requester_id:
                        supabase.table("notifications").insert(
                            {
                                "user_id": requester_id,
                                "title": "Donor Accepted Your Request",
                                "message": f"{donor_name} has accepted your emergency blood request! Fulfillment: {new_fulfilled}/{units_needed} units.",
                                "type": "request_update",
                                "reference_type": "blood_request",
                                "reference_id": request_id,
                                "is_read": False,
                                "created_at": now,
                            }
                        ).execute()
                except Exception as e:
                    logger.error("acceptance_notification_failed", error=str(e))

            # Update donor's total donations
            supabase.table("donors").update(
                {
                    "total_donations": donor_result.data.get("total_donations", 0) + 1,
                    "last_donation_date": now,
                    "updated_at": now,
                }
            ).eq("id", donor_id).execute()

    elif action.status == "declined":
        # Handle declined invitation: check if request needs status adjustment & notify requester
        if request_id:
            try:
                request_result = (
                    supabase.table("blood_requests")
                    .select("units_needed, units_fulfilled, status, requester_id")
                    .eq("id", request_id)
                    .maybe_single()
                    .execute()
                )

                if request_result and request_result.data:
                    req = request_result.data
                    requester_id = req.get("requester_id")

                    # Check remaining invitations for this request
                    inv_check = (
                        supabase.table("donor_invitations")
                        .select("status")
                        .eq("request_id", request_id)
                        .execute()
                    )
                    all_invs = inv_check.data or []
                    has_pending = any(i.get("status") == "pending" for i in all_invs)
                    has_accepted = any(i.get("status") == "accepted" for i in all_invs)

                    # If no units fulfilled and no pending or accepted remain, return to matching pool
                    if (req.get("units_fulfilled") or 0) == 0 and not has_pending and not has_accepted:
                        curr_status = req.get("status", "matching")
                        if curr_status in ["matched", "donor_confirmed"]:
                            supabase.table("blood_requests").update(
                                {
                                    "status": "matching",
                                    "updated_at": now,
                                }
                            ).eq("id", request_id).execute()

                            try:
                                supabase.table("request_status_history").insert({
                                    "request_id": request_id,
                                    "old_status": curr_status,
                                    "new_status": "matching",
                                    "changed_by": user_id,
                                    "notes": "All invitations declined; request returned to matching pool.",
                                    "created_at": now,
                                }).execute()
                            except Exception as e:
                                logger.warning("status_history_declined_failed", error=str(e))

                    # Notify requester of invitation update
                    if requester_id:
                        supabase.table("notifications").insert(
                            {
                                "user_id": requester_id,
                                "title": "Donor Invitation Update",
                                "message": "A prospective donor was unable to fulfill your blood request. BloodBridge AI continues active coordination.",
                                "type": "request_update",
                                "reference_type": "blood_request",
                                "reference_id": request_id,
                                "is_read": False,
                                "created_at": now,
                            }
                        ).execute()
            except Exception as e:
                logger.error("decline_handler_failed", error=str(e))

    logger.info(
        "invitation_responded",
        invitation_id=invitation_id,
        donor_id=donor_id,
        status=action.status,
    )

    return result.data[0]
