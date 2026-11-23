"""
Administration and governance API endpoints.
All endpoints require the 'admin' role.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from app.core.security import require_role
from app.schemas.admin import (
    AuditLogListResponse,
    DashboardStats,
    UserListResponse,
    UserManagementResponse,
    VerificationAction,
)
from app.schemas.auth import MessageResponse
from app.schemas.blood_bank import BloodBankResponse
from app.services.admin_service import (
    deactivate_user,
    get_audit_logs,
    get_dashboard_stats,
    get_inventory_overview,
    get_requests_by_area,
    get_requests_by_blood_group,
    list_users,
    verify_blood_bank,
    verify_user,
)

router = APIRouter(prefix="/api/admin", tags=["Admin Portal"])


@router.get("/stats", response_model=DashboardStats)
async def admin_stats(
    current_user: Dict[str, Any] = Depends(require_role("admin")),
) -> Dict[str, Any]:
    """Retrieve aggregate administrative operational statistics from live DB counts."""
    return await get_dashboard_stats()


@router.get("/users", response_model=UserListResponse)
async def admin_list_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    city: Optional[str] = Query(None, description="Filter by city"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification"),
    search: Optional[str] = Query(None, description="Search by name"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(require_role("admin")),
) -> Dict[str, Any]:
    """List and manage platform users."""
    res = await list_users(role=role, city=city, is_verified=is_verified, search=search, page=page, limit=limit)
    return {
        "users": res.get("items", []),
        "total": res.get("total", 0),
        "page": res.get("page", page),
        "limit": res.get("limit", limit),
        "has_more": res.get("has_more", False),
    }


@router.put("/users/{user_id}/verify", response_model=UserManagementResponse)
async def admin_verify_user(
    user_id: str,
    action: Optional[VerificationAction] = None,
    current_user: Dict[str, Any] = Depends(require_role("admin")),
) -> Dict[str, Any]:
    """Verify a registered donor or user."""
    return await verify_user(user_id, current_user["id"])


@router.put("/users/{user_id}/deactivate", response_model=UserManagementResponse)
async def admin_deactivate_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin")),
) -> Dict[str, Any]:
    """Deactivate a platform user account."""
    return await deactivate_user(user_id, current_user["id"])


@router.put("/blood-banks/{bank_id}/verify", response_model=BloodBankResponse)
async def admin_verify_blood_bank(
    bank_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin")),
) -> Dict[str, Any]:
    """Verify an institutional blood bank or hospital laboratory."""
    return await verify_blood_bank(bank_id, current_user["id"])


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def admin_audit_logs(
    resource_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(require_role("admin")),
) -> Dict[str, Any]:
    """Inspect secure system audit logs."""
    res = await get_audit_logs(resource_type=resource_type, action=action, page=page, limit=limit)
    return {
        "logs": res.get("items", []),
        "total": res.get("total", 0),
        "page": res.get("page", page),
        "limit": res.get("limit", limit),
        "has_more": res.get("has_more", False),
    }


@router.get("/analytics/requests-by-group")
async def analytics_by_group(
    current_user: Dict[str, Any] = Depends(require_role("admin")),
) -> List[Dict[str, Any]]:
    """Analytics: Blood requests segmented by blood group."""
    return await get_requests_by_blood_group()


@router.get("/analytics/requests-by-area")
async def analytics_by_area(
    current_user: Dict[str, Any] = Depends(require_role("admin")),
) -> List[Dict[str, Any]]:
    """Analytics: Blood requests segmented by Peshawar locality."""
    return await get_requests_by_area()


@router.get("/analytics/inventory-overview")
async def analytics_inventory_overview(
    current_user: Dict[str, Any] = Depends(require_role("admin")),
) -> List[Dict[str, Any]]:
    """Analytics: Blood bank stock distribution across verified institutions."""
    return await get_inventory_overview()
