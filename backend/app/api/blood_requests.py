"""
Blood requests API endpoints.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import ForbiddenError
from app.core.security import get_current_user, require_role
from app.matching.engine import find_matching_donors
from app.schemas.blood_request import (
    BloodRequestCreate,
    BloodRequestListResponse,
    BloodRequestResponse,
    BloodRequestUpdate,
)
from app.services.request_service import (
    cancel_blood_request,
    create_blood_request,
    get_blood_request,
    get_request_invitations,
    list_blood_requests,
    update_blood_request,
)

router = APIRouter(prefix="/api/blood-requests", tags=["Blood Requests"])


@router.post("/", response_model=BloodRequestResponse, status_code=201)
async def create_request(
    body: BloodRequestCreate,
    current_user: Dict[str, Any] = Depends(require_role("patient", "donor", "hospital", "blood_bank", "admin")),
) -> Dict[str, Any]:
    """Create a new blood donation request and trigger intelligent donor matching."""
    return await create_blood_request(current_user["id"], body)


@router.get("/", response_model=BloodRequestListResponse)
async def get_requests(
    blood_group: Optional[str] = Query(None, description="Filter by blood group"),
    emergency_level: Optional[str] = Query(None, description="critical, urgent, normal"),
    status: Optional[str] = Query(None, description="Filter by request status"),
    area: Optional[str] = Query(None, description="Filter by Peshawar area"),
    city: Optional[str] = Query(None, description="Filter by city"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """List public blood requests with filters."""
    return await list_blood_requests(
        blood_group=blood_group,
        emergency_level=emergency_level,
        status=status,
        area=area,
        city=city,
        page=page,
        limit=limit,
    )


@router.get("/my-requests", response_model=BloodRequestListResponse)
async def get_my_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """List blood requests created by the current authenticated user."""
    return await list_blood_requests(
        requester_id=current_user["id"],
        page=page,
        limit=limit,
    )


@router.get("/{request_id}", response_model=BloodRequestResponse)
async def get_request_by_id(
    request_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get single blood request details and match counts."""
    user_id = current_user["id"] if current_user else None
    return await get_blood_request(request_id, user_id=user_id)


@router.put("/{request_id}", response_model=BloodRequestResponse)
async def update_request(
    request_id: str,
    body: BloodRequestUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update status or details of a blood request."""
    return await update_blood_request(request_id, current_user["id"], current_user.get("role", "patient"), body)


@router.put("/{request_id}/cancel", response_model=BloodRequestResponse)
async def cancel_request(
    request_id: str,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Cancel an active blood request."""
    return await cancel_blood_request(request_id, current_user["id"], current_user.get("role", "patient"), reason)


@router.get("/{request_id}/invitations")
async def get_invitations_for_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Get list of donor invitations issued for this request."""
    return await get_request_invitations(request_id, current_user["id"], current_user.get("role", "patient"))


@router.post("/{request_id}/match")
async def trigger_matching(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Explicitly trigger or re-run the Python intelligent matching engine."""
    request_record = await get_blood_request(request_id)
    if request_record.get("requester_id") != current_user["id"] and current_user.get("role") != "admin":
        raise ForbiddenError("Not authorized to trigger matching for this request")

    results = await find_matching_donors(request_id)
    return {
        "request_id": request_id,
        "matched_count": len(results),
        "matches": [r.to_dict() for r in results],
    }
