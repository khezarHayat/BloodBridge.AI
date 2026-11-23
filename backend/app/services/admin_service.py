"""
Admin management and analytics service.

Provides system overview statistics, user verification, institutional reviews,
audit log queries, and real aggregate analytics.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.core.supabase_client import get_supabase_admin
from app.utils.audit import log_audit
from app.utils.pagination import paginate_response

logger = get_logger(__name__)


async def get_dashboard_stats() -> Dict[str, Any]:
    """
    Fetch live statistics from the database for the administration overview.
    All figures are derived directly from PostgreSQL counts.
    """
    supabase = get_supabase_admin()

    users_res = supabase.table("profiles").select("id", count="exact").execute()
    total_users = users_res.count or 0

    donors_res = supabase.table("donors").select("id", count="exact").execute()
    total_donors = donors_res.count or 0

    verified_donors_res = supabase.table("donors").select("id", count="exact").not_.is_("verified_at", "null").execute()
    verified_donors = verified_donors_res.count or 0

    active_req_res = (
        supabase.table("blood_requests")
        .select("id", count="exact")
        .in_("status", ["pending", "matching", "matched"])
        .execute()
    )
    active_requests = active_req_res.count or 0

    comp_req_res = supabase.table("blood_requests").select("id", count="exact").eq("status", "fulfilled").execute()
    completed_requests = comp_req_res.count or 0

    banks_res = supabase.table("blood_banks").select("id", count="exact").execute()
    registered_blood_banks = banks_res.count or 0

    pending_banks_res = supabase.table("blood_banks").select("id", count="exact").eq("is_verified", False).execute()
    pending_verifications = pending_banks_res.count or 0

    return {
        "total_users": total_users,
        "total_donors": total_donors,
        "verified_donors": verified_donors,
        "active_requests": active_requests,
        "completed_requests": completed_requests,
        "registered_blood_banks": registered_blood_banks,
        "pending_verifications": pending_verifications,
    }


async def list_users(
    role: Optional[str] = None,
    city: Optional[str] = None,
    is_verified: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> Dict[str, Any]:
    """List all registered users with role and status filtering."""
    supabase = get_supabase_admin()
    offset = (page - 1) * limit

    query = supabase.table("profiles").select("*", count="exact")
    if role:
        query = query.eq("role", role)
    if city:
        query = query.eq("city", city)
    if is_verified is not None:
        query = query.eq("is_verified", is_verified)
    if search:
        query = query.ilike("full_name", f"%{search}%")

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    res = query.execute()

    profiles = res.data or []
    total = res.count if res.count is not None else len(profiles)
    return paginate_response(profiles, total, page, limit)


async def verify_user(user_id: str, admin_id: str) -> Dict[str, Any]:
    """Mark a user profile and any associated donor record as verified."""
    supabase = get_supabase_admin()
    now = datetime.now(timezone.utc).isoformat()

    p_res = supabase.table("profiles").update({"is_verified": True, "updated_at": now}).eq("id", user_id).execute()
    if not p_res.data:
        raise NotFoundError("User not found")

    # If user is a donor, also update donor verification fields
    supabase.table("donors").update({
        "verified_at": now,
        "verified_by": admin_id,
        "is_eligible": True,
        "updated_at": now,
    }).eq("user_id", user_id).execute()

    await log_audit(
        user_id=admin_id,
        action="VERIFY_USER",
        resource_type="profiles",
        resource_id=user_id,
        details={"status": "verified"},
    )
    return p_res.data[0]


async def deactivate_user(user_id: str, admin_id: str) -> Dict[str, Any]:
    """Deactivate a user account."""
    supabase = get_supabase_admin()
    now = datetime.now(timezone.utc).isoformat()

    p_res = supabase.table("profiles").update({"is_active": False, "updated_at": now}).eq("id", user_id).execute()
    if not p_res.data:
        raise NotFoundError("User not found")

    await log_audit(
        user_id=admin_id,
        action="DEACTIVATE_USER",
        resource_type="profiles",
        resource_id=user_id,
        details={"status": "deactivated"},
    )
    return p_res.data[0]


async def verify_blood_bank(bank_id: str, admin_id: str) -> Dict[str, Any]:
    """Approve and verify a blood bank or hospital facility."""
    supabase = get_supabase_admin()
    now = datetime.now(timezone.utc).isoformat()

    res = supabase.table("blood_banks").update({
        "is_verified": True,
        "verified_at": now,
        "verified_by": admin_id,
        "updated_at": now,
    }).eq("id", bank_id).execute()

    if not res.data:
        raise NotFoundError("Blood bank not found")

    await log_audit(
        user_id=admin_id,
        action="VERIFY_BLOOD_BANK",
        resource_type="blood_banks",
        resource_id=bank_id,
        details={"status": "verified"},
    )
    return res.data[0]


async def get_audit_logs(
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    page: int = 1,
    limit: int = 25,
) -> Dict[str, Any]:
    """Retrieve system audit logs for administrative inspection."""
    supabase = get_supabase_admin()
    offset = (page - 1) * limit

    query = supabase.table("audit_logs").select("*, profiles:user_id(full_name, email)", count="exact")
    if resource_type:
        query = query.eq("resource_type", resource_type)
    if action:
        query = query.eq("action", action)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    res = query.execute()

    logs = res.data or []
    for l in logs:
        p = l.get("profiles")
        if isinstance(p, dict):
            l["user_name"] = p.get("full_name")
            l["user_email"] = p.get("email")

    total = res.count if res.count is not None else len(logs)
    return paginate_response(logs, total, page, limit)


async def get_requests_by_blood_group() -> List[Dict[str, Any]]:
    """Aggregate total blood requests grouped by required blood group."""
    supabase = get_supabase_admin()
    res = supabase.table("blood_requests").select("blood_group").execute()
    data = res.data or []

    groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    counts = {g: 0 for g in groups}
    for item in data:
        bg = item.get("blood_group")
        if bg in counts:
            counts[bg] += 1

    return [{"blood_group": bg, "count": count} for bg, count in counts.items()]


async def get_requests_by_area() -> List[Dict[str, Any]]:
    """Aggregate blood requests grouped by Peshawar area."""
    supabase = get_supabase_admin()
    res = supabase.table("blood_requests").select("area").execute()
    data = res.data or []

    areas: Dict[str, int] = {}
    for item in data:
        a = item.get("area") or "Unknown"
        areas[a] = areas.get(a, 0) + 1

    return [{"area": area, "count": count} for area, count in sorted(areas.items(), key=lambda x: x[1], reverse=True)]


async def get_inventory_overview() -> List[Dict[str, Any]]:
    """Aggregate total available inventory across all verified Peshawar blood banks."""
    supabase = get_supabase_admin()
    today = datetime.now(timezone.utc).date().isoformat()

    res = (
        supabase.table("inventory_batches")
        .select("blood_group, units_available")
        .eq("availability_status", "available")
        .gte("expiry_date", today)
        .execute()
    )
    batches = res.data or []

    groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    units = {g: 0 for g in groups}
    for b in batches:
        bg = b.get("blood_group")
        u = b.get("units_available", 0)
        if bg in units:
            units[bg] += u

    return [{"blood_group": bg, "total_units": count} for bg, count in units.items()]
