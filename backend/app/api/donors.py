"""
Donor API endpoints.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, Request

from app.core.exceptions import NotFoundError
from app.core.security import get_current_user, require_role
from app.core.supabase_client import get_supabase_admin
from app.schemas.donor import (
    DonorAvailabilityToggle,
    DonorCreate,
    DonorListResponse,
    DonorResponse,
    DonorUpdate,
)
from app.schemas.invitation import InvitationAction, InvitationResponse
from app.services.donor_service import (
    create_donor,
    get_donor,
    get_donor_invitations,
    list_donors,
    respond_to_invitation,
    toggle_availability,
    update_donor,
)

router = APIRouter(prefix="/api/donors", tags=["Donors"])


@router.get("/", response_model=DonorListResponse)
async def get_donors(
    blood_group: Optional[str] = Query(None, description="Filter by blood group"),
    area: Optional[str] = Query(None, description="Filter by area in Peshawar"),
    city: Optional[str] = Query(None, description="Filter by city"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """Public discovery endpoint to list available blood donors in Peshawar (without exposing contact info)."""
    return await list_donors(
        blood_group=blood_group,
        area=area,
        city=city,
        is_available=is_available,
        page=page,
        limit=limit,
    )


@router.get("/me/profile", response_model=DonorResponse)
async def get_my_donor_profile(
    current_user: Dict[str, Any] = Depends(require_role("donor", "admin")),
) -> Dict[str, Any]:
    """Get the current authenticated user's donor profile."""
    supabase = get_supabase_admin()
    res = (
        supabase.table("donors")
        .select("id")
        .eq("user_id", current_user["id"])
        .maybe_single()
        .execute()
    )
    if not res or not res.data:
        raise NotFoundError("Donor profile not found for this user")
    return await get_donor(res.data["id"])


@router.get("/me/invitations")
async def get_my_invitations(
    current_user: Dict[str, Any] = Depends(require_role("donor", "admin")),
) -> Dict[str, Any]:
    """Get blood donation invitations matching this donor."""
    return await get_donor_invitations(current_user["id"])


@router.put("/invitations/{invitation_id}", response_model=InvitationResponse)
async def respond_invitation(
    invitation_id: str,
    action: InvitationAction,
    current_user: Dict[str, Any] = Depends(require_role("donor", "admin")),
) -> Dict[str, Any]:
    """Accept or decline an emergency blood donation request invitation."""
    return await respond_to_invitation(invitation_id, current_user["id"], action)


@router.get("/{donor_id}", response_model=DonorResponse)
async def get_donor_by_id(donor_id: str) -> Dict[str, Any]:
    """Get donor public summary by donor ID."""
    return await get_donor(donor_id)


@router.post("/", response_model=DonorResponse, status_code=201)
async def register_donor_profile(
    body: DonorCreate,
    current_user: Dict[str, Any] = Depends(require_role("donor", "admin")),
) -> Dict[str, Any]:
    """Create or complete donor medical profile."""
    record = await create_donor(current_user["id"], body)
    return await get_donor(record["id"])


@router.put("/{donor_id}", response_model=DonorResponse)
async def update_donor_profile(
    donor_id: str,
    body: DonorUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update donor medical or contact details."""
    record = await update_donor(donor_id, current_user["id"], body)
    return await get_donor(record["id"])


@router.patch("/{donor_id}/availability", response_model=DonorResponse)
async def set_donor_availability(
    donor_id: str,
    body: DonorAvailabilityToggle,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Toggle donor availability status."""
    record = await toggle_availability(donor_id, current_user["id"], body.is_available)
    return await get_donor(record["id"])
