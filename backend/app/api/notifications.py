"""
In-app notifications API endpoints.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user
from app.schemas.auth import MessageResponse
from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.services.notification_service import (
    get_notifications,
    get_unread_count,
    mark_all_read,
    mark_read,
)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("/", response_model=NotificationListResponse)
async def list_user_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get notifications for the authenticated user."""
    res = await get_notifications(current_user["id"], page=page, limit=limit, unread_only=unread_only)
    unread = await get_unread_count(current_user["id"])
    return {
        "notifications": res.get("items", []),
        "total": res.get("total", 0),
        "page": res.get("page", page),
        "limit": res.get("limit", limit),
        "has_more": res.get("has_more", False),
        "unread_count": unread,
    }


@router.get("/unread-count", response_model=UnreadCountResponse)
async def unread_count_endpoint(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get the number of unread notifications for the active user."""
    count = await get_unread_count(current_user["id"])
    return {"unread_count": count}


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_single_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Mark an individual notification as read."""
    return await mark_read(notification_id, current_user["id"])


@router.put("/read-all", response_model=MessageResponse)
async def mark_all_as_read(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Mark all notifications as read."""
    updated = await mark_all_read(current_user["id"])
    return {"message": f"{updated} notifications marked as read", "success": True}
