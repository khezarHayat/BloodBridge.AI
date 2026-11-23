"""
Blood banks and hospital facilities API endpoints.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import NotFoundError
from app.core.security import get_current_user, require_role
from app.schemas.auth import MessageResponse
from app.schemas.blood_bank import (
    BloodBankCreate,
    BloodBankListResponse,
    BloodBankResponse,
    BloodBankUpdate,
    InventoryBatchCreate,
    InventoryBatchListResponse,
    InventoryBatchResponse,
    InventoryBatchUpdate,
    InventorySummary,
)
from app.services.blood_bank_service import (
    add_inventory_batch,
    delete_inventory_batch,
    get_blood_bank,
    get_blood_bank_by_user_id,
    get_inventory,
    get_inventory_summary,
    list_blood_banks,
    register_blood_bank,
    update_blood_bank,
    update_inventory_batch,
)

router = APIRouter(prefix="/api/blood-banks", tags=["Blood Banks & Inventory"])


@router.get("/", response_model=BloodBankListResponse)
async def get_blood_banks(
    city: Optional[str] = Query(None, description="Filter by city"),
    area: Optional[str] = Query(None, description="Filter by area"),
    is_verified: Optional[bool] = Query(None, description="Filter verified only"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """List registered blood banks and hospital centers in Peshawar."""
    return await list_blood_banks(city=city, area=area, is_verified=is_verified, page=page, limit=limit)


@router.get("/me", response_model=BloodBankResponse)
async def get_my_blood_bank(
    current_user: Dict[str, Any] = Depends(require_role("blood_bank", "hospital", "admin")),
) -> Dict[str, Any]:
    """Get blood bank profile belonging to the current authenticated institutional user."""
    bank = await get_blood_bank_by_user_id(current_user["id"])
    if not bank:
        raise NotFoundError("No blood bank profile linked to this account")
    return bank


@router.get("/{bank_id}", response_model=BloodBankResponse)
async def get_bank_details(bank_id: str) -> Dict[str, Any]:
    """Get details of a blood bank or hospital facility."""
    return await get_blood_bank(bank_id)


@router.post("/", response_model=BloodBankResponse, status_code=201)
async def create_bank(
    body: BloodBankCreate,
    current_user: Dict[str, Any] = Depends(require_role("blood_bank", "hospital", "admin")),
) -> Dict[str, Any]:
    """Register a new blood bank facility."""
    return await register_blood_bank(current_user["id"], body)


@router.put("/{bank_id}", response_model=BloodBankResponse)
async def update_bank(
    bank_id: str,
    body: BloodBankUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update blood bank facility details."""
    return await update_blood_bank(bank_id, current_user["id"], current_user.get("role", "blood_bank"), body)


@router.get("/{bank_id}/inventory", response_model=InventoryBatchListResponse)
async def get_bank_inventory(
    bank_id: str,
    blood_group: Optional[str] = Query(None, description="Filter by blood group"),
    available_only: bool = Query(True, description="Filter valid available units"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> Dict[str, Any]:
    """Get inventory batches for a blood bank."""
    return await get_inventory(bank_id, blood_group=blood_group, available_only=available_only, page=page, limit=limit)


@router.post("/{bank_id}/inventory", response_model=InventoryBatchResponse, status_code=201)
async def add_batch(
    bank_id: str,
    body: InventoryBatchCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Add a new blood batch to facility inventory."""
    return await add_inventory_batch(bank_id, current_user["id"], current_user.get("role", "blood_bank"), body)


@router.put("/{bank_id}/inventory/{batch_id}", response_model=InventoryBatchResponse)
async def update_batch(
    bank_id: str,
    batch_id: str,
    body: InventoryBatchUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update inventory batch (available units or status)."""
    return await update_inventory_batch(bank_id, batch_id, current_user["id"], current_user.get("role", "blood_bank"), body)


@router.delete("/{bank_id}/inventory/{batch_id}", response_model=MessageResponse)
async def delete_batch(
    bank_id: str,
    batch_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Delete an inventory batch."""
    await delete_inventory_batch(bank_id, batch_id, current_user["id"], current_user.get("role", "blood_bank"))
    return {"message": "Inventory batch deleted", "success": True}


@router.get("/{bank_id}/inventory/summary", response_model=List[InventorySummary])
async def get_summary(bank_id: str) -> List[Dict[str, Any]]:
    """Get aggregated units available by blood group."""
    return await get_inventory_summary(bank_id)
