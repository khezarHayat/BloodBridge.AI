"""
Blood request service.

Handles blood request creation, retrieval, updates, status transitions,
and integrates with the intelligent matching engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.core.supabase_client import get_supabase_admin
from app.matching.engine import find_matching_donors
from app.schemas.blood_request import BloodRequestCreate, BloodRequestUpdate
from app.utils.audit import log_audit
from app.utils.pagination import get_count_from_response, paginate_response

logger = get_logger(__name__)


def _generate_request_number() -> str:
    """Generate a readable request number like BR-202611-ABCD."""
    random_part = uuid.uuid4().hex[:6].upper()
    now_part = datetime.now(timezone.utc).strftime("%y%m")
    return f"BR-{now_part}-{random_part}"


async def create_blood_request(user_id: str, data: BloodRequestCreate) -> Dict[str, Any]:
    """
    Create a new emergency or standard blood request.

    Stores the request in Supabase, triggers the intelligent matching engine,
    invites compatible donors, and logs audit entries.

    Args:
        user_id: The authenticated requester's profile ID.
        data: Blood request input schema.

    Returns:
        The created blood request record with initial matching stats.
    """
    supabase = get_supabase_admin()
    now = datetime.now(timezone.utc).isoformat()
    req_number = _generate_request_number()

    record_data = {
        "request_number": req_number,
        "requester_id": user_id,
        "patient_name": data.patient_name,
        "blood_group": data.blood_group,
        "units_needed": data.units_needed,
        "units_fulfilled": 0,
        "hospital_name": data.hospital_name,
        "hospital_address": data.hospital_address,
        "city": data.city or "Peshawar",
        "area": data.area,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "emergency_level": data.emergency_level,
        "required_by": data.required_by.isoformat() if data.required_by else None,
        "contact_name": data.contact_name,
        "contact_phone": data.contact_phone,
        "additional_notes": data.additional_notes,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    }

    try:
        res = supabase.table("blood_requests").insert(record_data).execute()
        if not res.data:
            raise ValidationError("Failed to create blood request record")
        request_record = res.data[0]
        request_id = request_record["id"]
    except Exception as e:
        logger.error("create_blood_request_error", error=str(e), user_id=user_id)
        raise ValidationError(f"Error creating blood request: {str(e)}")

    # Record status history
    try:
        supabase.table("request_status_history").insert({
            "request_id": request_id,
            "old_status": None,
            "new_status": "pending",
            "changed_by": user_id,
            "notes": "Request initiated by patient/requester",
            "created_at": now,
        }).execute()
    except Exception as e:
        logger.warning("status_history_creation_failed", error=str(e))

    # Audit log
    await log_audit(
        user_id=user_id,
        action="CREATE_BLOOD_REQUEST",
        resource_type="blood_requests",
        resource_id=request_id,
        details={"blood_group": data.blood_group, "units_needed": data.units_needed, "emergency_level": data.emergency_level},
    )

    # Automatically trigger matching engine
    try:
        matched_results = await find_matching_donors(request_id)
        request_record["matched_donors"] = len(matched_results)
    except Exception as e:
        logger.error("matching_trigger_failed", error=str(e), request_id=request_id)
        request_record["matched_donors"] = 0

    return request_record


async def get_blood_request(request_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch details of a single blood request.

    Args:
        request_id: UUID of the blood request.
        user_id: Optional ID of the user requesting to view.

    Returns:
        Blood request record with requester profile info and match counts.
    """
    supabase = get_supabase_admin()
    res = supabase.table("blood_requests").select(
        "*, profiles:requester_id(full_name, phone, email)"
    ).eq("id", request_id).maybe_single().execute()

    if not res or not res.data:
        raise NotFoundError("Blood request not found")

    record = res.data
    # Flatten requester name
    profiles_data = record.get("profiles")
    if isinstance(profiles_data, dict):
        record["requester_name"] = profiles_data.get("full_name")

    # Count matched donor invitations
    inv_res = supabase.table("donor_invitations").select("id", count="exact").eq("request_id", request_id).execute()
    record["matched_donors"] = inv_res.count if inv_res and inv_res.count is not None else 0

    return record


async def list_blood_requests(
    user_id: Optional[str] = None,
    requester_id: Optional[str] = None,
    blood_group: Optional[str] = None,
    emergency_level: Optional[str] = None,
    status: Optional[str] = None,
    city: Optional[str] = None,
    area: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    List blood requests with filtering and pagination.
    """
    supabase = get_supabase_admin()
    offset = (page - 1) * limit

    query = supabase.table("blood_requests").select(
        "*, profiles:requester_id(full_name)", count="exact"
    )

    if requester_id:
        query = query.eq("requester_id", requester_id)
    if blood_group:
        query = query.eq("blood_group", blood_group)
    if emergency_level:
        query = query.eq("emergency_level", emergency_level)
    if status:
        query = query.eq("status", status)
    if city:
        query = query.eq("city", city)
    if area:
        query = query.eq("area", area)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    result = query.execute()

    requests = result.data or []
    for req in requests:
        profiles_data = req.get("profiles")
        if isinstance(profiles_data, dict):
            req["requester_name"] = profiles_data.get("full_name")

    total = result.count if result.count is not None else len(requests)
    return paginate_response(requests, total, page, limit)


async def update_blood_request(
    request_id: str, user_id: str, role: str, data: BloodRequestUpdate
) -> Dict[str, Any]:
    """
    Update blood request status or fulfilled units.
    """
    supabase = get_supabase_admin()
    existing = await get_blood_request(request_id)

    # Permission check: Requester or Admin
    if existing["requester_id"] != user_id and role != "admin":
        raise ForbiddenError("You are not authorized to update this blood request")

    now = datetime.now(timezone.utc).isoformat()
    update_data: Dict[str, Any] = {"updated_at": now}

    old_status = existing["status"]
    if data.status and data.status != old_status:
        update_data["status"] = data.status
        if data.status == "fulfilled":
            update_data["fulfilled_at"] = now
        elif data.status == "cancelled":
            update_data["cancelled_at"] = now
            if data.cancellation_reason:
                update_data["cancellation_reason"] = data.cancellation_reason

    if data.units_fulfilled is not None:
        update_data["units_fulfilled"] = data.units_fulfilled

    if data.additional_notes is not None:
        update_data["additional_notes"] = data.additional_notes

    res = supabase.table("blood_requests").update(update_data).eq("id", request_id).execute()
    if not res.data:
        raise ValidationError("Failed to update blood request")

    # If status changed, record history
    if data.status and data.status != old_status:
        try:
            supabase.table("request_status_history").insert({
                "request_id": request_id,
                "old_status": old_status,
                "new_status": data.status,
                "changed_by": user_id,
                "notes": f"Status updated to {data.status}",
                "created_at": now,
            }).execute()
        except Exception as e:
            logger.warning("status_history_log_failed", error=str(e))

    await log_audit(
        user_id=user_id,
        action="UPDATE_BLOOD_REQUEST",
        resource_type="blood_requests",
        resource_id=request_id,
        details=update_data,
    )

    return res.data[0]


async def cancel_blood_request(
    request_id: str, user_id: str, role: str, reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cancel an active blood request.
    """
    update_schema = BloodRequestUpdate(
        status="cancelled",
        cancellation_reason=reason or "Cancelled by user"
    )
    return await update_blood_request(request_id, user_id, role, update_schema)


def _mask_donor_name(name: Optional[str]) -> str:
    """Mask donor's full name for patient privacy protection (e.g. Tariq Afridi -> Tariq A.)."""
    if not name:
        return "Volunteer Donor"
    parts = name.strip().split()
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} {parts[-1][0]}."


async def get_request_invitations(request_id: str, user_id: str, role: str) -> List[Dict[str, Any]]:
    """
    Get donor invitations for a specific request.
    Only requester, invited donor, or admin can see them.
    Protects donor privacy by masking full names and strictly omitting contact details.
    """
    supabase = get_supabase_admin()
    existing = await get_blood_request(request_id)

    if existing["requester_id"] != user_id and role != "admin":
        raise ForbiddenError("Not authorized to view invitations for this request")

    res = supabase.table("donor_invitations").select(
        "id, request_id, donor_id, status, match_score, match_reasons, distance_km, invited_at, responded_at, donors:donor_id(blood_group, profiles:user_id(full_name, area))"
    ).eq("request_id", request_id).order("match_score", desc=True).execute()

    raw_items = res.data or []
    sanitized_invitations = []
    for item in raw_items:
        donor_rel = item.get("donors") or {}
        profile_rel = donor_rel.get("profiles") or {}
        raw_name = profile_rel.get("full_name")
        masked_name = _mask_donor_name(raw_name)
        blood_group = donor_rel.get("blood_group")
        area = profile_rel.get("area")

        sanitized_invitations.append({
            "id": item["id"],
            "request_id": item["request_id"],
            "donor_id": item["donor_id"],
            "status": item["status"],
            "match_score": float(item["match_score"]) if item.get("match_score") is not None else 0.0,
            "match_reasons": item.get("match_reasons") or [],
            "distance_km": float(item["distance_km"]) if item.get("distance_km") is not None else None,
            "invited_at": item.get("invited_at"),
            "responded_at": item.get("responded_at"),
            "donor_name": masked_name,
            "donor_blood_group": blood_group,
            "donor_area": area,
            "donors": {
                "blood_group": blood_group,
                "profiles": {
                    "full_name": masked_name,
                    "area": area,
                },
            },
        })

    return sanitized_invitations
