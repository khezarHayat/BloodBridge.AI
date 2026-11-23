"""
Blood bank and hospital inventory service.

Handles institutional profile management, blood inventory batch tracking,
expiration monitoring, and inventory summaries.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.core.supabase_client import get_supabase_admin
from app.schemas.blood_bank import (
    BloodBankCreate,
    BloodBankUpdate,
    InventoryBatchCreate,
    InventoryBatchUpdate,
)
from app.utils.audit import log_audit
from app.utils.pagination import paginate_response

logger = get_logger(__name__)


async def register_blood_bank(user_id: str, data: BloodBankCreate) -> Dict[str, Any]:
    """
    Register a new blood bank or hospital facility.
    """
    supabase = get_supabase_admin()
    now = datetime.now(timezone.utc).isoformat()

    record_data = {
        "user_id": user_id,
        "name": data.name,
        "license_number": data.license_number,
        "type": data.type,
        "phone": data.phone,
        "email": data.email,
        "address": data.address,
        "city": data.city or "Peshawar",
        "area": data.area,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "operating_hours": data.operating_hours,
        "is_verified": False,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    res = supabase.table("blood_banks").insert(record_data).execute()
    if not res.data:
        raise ValidationError("Failed to register blood bank")

    bank = res.data[0]
    await log_audit(
        user_id=user_id,
        action="REGISTER_BLOOD_BANK",
        resource_type="blood_banks",
        resource_id=bank["id"],
        details={"name": data.name, "license": data.license_number},
    )
    return bank


async def get_blood_bank(bank_id: str) -> Dict[str, Any]:
    """Get blood bank details by ID."""
    supabase = get_supabase_admin()
    res = supabase.table("blood_banks").select("*").eq("id", bank_id).maybe_single().execute()
    if not res or not res.data:
        raise NotFoundError("Blood bank not found")
    return res.data


async def get_blood_bank_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get blood bank associated with a specific user profile."""
    supabase = get_supabase_admin()
    res = supabase.table("blood_banks").select("*").eq("user_id", user_id).maybe_single().execute()
    return res.data if res and res.data else None


async def list_blood_banks(
    city: Optional[str] = None,
    area: Optional[str] = None,
    is_verified: Optional[bool] = None,
    page: int = 1,
    limit: int = 20,
) -> Dict[str, Any]:
    """List blood banks with filtering."""
    supabase = get_supabase_admin()
    offset = (page - 1) * limit

    query = supabase.table("blood_banks").select("*", count="exact")
    if city:
        query = query.eq("city", city)
    if area:
        query = query.eq("area", area)
    if is_verified is not None:
        query = query.eq("is_verified", is_verified)

    query = query.order("name", desc=False).range(offset, offset + limit - 1)
    res = query.execute()

    banks = res.data or []
    total = res.count if res.count is not None else len(banks)
    return paginate_response(banks, total, page, limit)


async def update_blood_bank(
    bank_id: str, user_id: str, role: str, data: BloodBankUpdate
) -> Dict[str, Any]:
    """Update blood bank profile details."""
    supabase = get_supabase_admin()
    bank = await get_blood_bank(bank_id)

    if bank["user_id"] != user_id and role != "admin":
        raise ForbiddenError("Not authorized to update this blood bank")

    now = datetime.now(timezone.utc).isoformat()
    update_data: Dict[str, Any] = {"updated_at": now}
    for field, val in data.model_dump(exclude_unset=True).items():
        if val is not None:
            update_data[field] = val

    res = supabase.table("blood_banks").update(update_data).eq("id", bank_id).execute()
    if not res.data:
        raise ValidationError("Failed to update blood bank")

    return res.data[0]


async def add_inventory_batch(
    bank_id: str, user_id: str, role: str, data: InventoryBatchCreate
) -> Dict[str, Any]:
    """
    Add a new verified blood batch to the blood bank inventory.
    """
    supabase = get_supabase_admin()
    bank = await get_blood_bank(bank_id)

    if bank["user_id"] != user_id and role != "admin":
        raise ForbiddenError("Not authorized to modify inventory for this blood bank")

    if data.expiry_date <= data.collection_date:
        raise ValidationError("Expiry date must be after collection date")

    today = date.today()
    if data.expiry_date <= today:
        raise ValidationError("Cannot add already expired blood batch")

    now = datetime.now(timezone.utc).isoformat()
    record_data = {
        "blood_bank_id": bank_id,
        "blood_group": data.blood_group,
        "units_available": data.units_available,
        "collection_date": data.collection_date.isoformat(),
        "expiry_date": data.expiry_date.isoformat(),
        "screening_status": data.screening_status,
        "availability_status": "available",
        "batch_number": data.batch_number,
        "created_at": now,
        "updated_at": now,
    }

    res = supabase.table("inventory_batches").insert(record_data).execute()
    if not res.data:
        raise ValidationError("Failed to add inventory batch")

    batch = res.data[0]
    await log_audit(
        user_id=user_id,
        action="ADD_INVENTORY_BATCH",
        resource_type="inventory_batches",
        resource_id=batch["id"],
        details={"blood_group": data.blood_group, "units": data.units_available},
    )
    return batch


async def update_inventory_batch(
    bank_id: str, batch_id: str, user_id: str, role: str, data: InventoryBatchUpdate
) -> Dict[str, Any]:
    """Update units or status of an existing inventory batch."""
    supabase = get_supabase_admin()
    bank = await get_blood_bank(bank_id)

    if bank["user_id"] != user_id and role != "admin":
        raise ForbiddenError("Not authorized to modify this inventory")

    now = datetime.now(timezone.utc).isoformat()
    update_data: Dict[str, Any] = {"updated_at": now}
    for field, val in data.model_dump(exclude_unset=True).items():
        if val is not None:
            update_data[field] = val

    res = supabase.table("inventory_batches").update(update_data).eq("id", batch_id).eq("blood_bank_id", bank_id).execute()
    if not res.data:
        raise NotFoundError("Inventory batch not found or failed to update")

    return res.data[0]


async def delete_inventory_batch(
    bank_id: str, batch_id: str, user_id: str, role: str
) -> bool:
    """Delete an inventory batch."""
    supabase = get_supabase_admin()
    bank = await get_blood_bank(bank_id)

    if bank["user_id"] != user_id and role != "admin":
        raise ForbiddenError("Not authorized to delete this inventory batch")

    res = supabase.table("inventory_batches").delete().eq("id", batch_id).eq("blood_bank_id", bank_id).execute()
    return bool(res.data)


async def get_inventory(
    bank_id: str,
    blood_group: Optional[str] = None,
    available_only: bool = True,
    page: int = 1,
    limit: int = 50,
) -> Dict[str, Any]:
    """Get inventory batches for a blood bank with automatic expiry detection."""
    supabase = get_supabase_admin()
    offset = (page - 1) * limit
    today = date.today().isoformat()

    query = supabase.table("inventory_batches").select("*", count="exact").eq("blood_bank_id", bank_id)
    if blood_group:
        query = query.eq("blood_group", blood_group)
    if available_only:
        query = query.eq("availability_status", "available").gt("units_available", 0).gte("expiry_date", today)

    query = query.order("expiry_date", desc=False).range(offset, offset + limit - 1)
    res = query.execute()

    batches = res.data or []
    total = res.count if res.count is not None else len(batches)
    return paginate_response(batches, total, page, limit)


async def get_inventory_summary(bank_id: str) -> List[Dict[str, Any]]:
    """
    Get aggregated available units per blood group for a blood bank.
    Never includes expired or quarantined blood.
    """
    supabase = get_supabase_admin()
    today = date.today().isoformat()

    res = supabase.table("inventory_batches").select(
        "blood_group, units_available"
    ).eq("blood_bank_id", bank_id).eq("availability_status", "available").gte("expiry_date", today).execute()

    batches = res.data or []
    groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    summary_map = {g: 0 for g in groups}

    for b in batches:
        bg = b.get("blood_group")
        units = b.get("units_available", 0)
        if bg in summary_map:
            summary_map[bg] += units

    return [
        {"blood_group": bg, "total_units": count, "available_units": count}
        for bg, count in summary_map.items()
    ]
