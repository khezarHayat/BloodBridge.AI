"""
Notification service.

Handles creating in-app alerts, marking as read, unread counts,
and dispatching donor invitation notifications.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.core.supabase_client import get_supabase_admin
from app.utils.pagination import paginate_response

logger = get_logger(__name__)


async def create_notification(
    user_id: str,
    title: str,
    message: str,
    type: str = "system",
    reference_type: Optional[str] = None,
    reference_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a notification entry in the database.
    """
    supabase = get_supabase_admin()
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": type,
        "reference_type": reference_type,
        "reference_id": reference_id,
        "is_read": False,
        "created_at": now,
    }

    res = supabase.table("notifications").insert(record).execute()
    if not res.data:
        raise ValidationError("Failed to create notification")
    return res.data[0]


async def get_notifications(
    user_id: str,
    page: int = 1,
    limit: int = 20,
    unread_only: bool = False,
) -> Dict[str, Any]:
    """
    Get user notifications with pagination.
    """
    supabase = get_supabase_admin()
    offset = (page - 1) * limit

    query = supabase.table("notifications").select("*", count="exact").eq("user_id", user_id)
    if unread_only:
        query = query.eq("is_read", False)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    res = query.execute()

    notifications = res.data or []
    total = res.count if res.count is not None else len(notifications)
    return paginate_response(notifications, total, page, limit)


async def mark_read(notification_id: str, user_id: str) -> Dict[str, Any]:
    """Mark a specific notification as read."""
    supabase = get_supabase_admin()
    now = datetime.now(timezone.utc).isoformat()

    res = (
        supabase.table("notifications")
        .update({"is_read": True, "read_at": now})
        .eq("id", notification_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not res.data:
        raise NotFoundError("Notification not found")
    return res.data[0]


async def mark_all_read(user_id: str) -> int:
    """Mark all unread notifications as read for a user."""
    supabase = get_supabase_admin()
    now = datetime.now(timezone.utc).isoformat()

    res = (
        supabase.table("notifications")
        .update({"is_read": True, "read_at": now})
        .eq("user_id", user_id)
        .eq("is_read", False)
        .execute()
    )
    return len(res.data) if res and res.data else 0


async def get_unread_count(user_id: str) -> int:
    """Get the number of unread notifications for a user."""
    supabase = get_supabase_admin()
    res = (
        supabase.table("notifications")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .eq("is_read", False)
        .execute()
    )
    return res.count if res and res.count is not None else 0


async def notify_donors_of_request(
    user_ids: List[str],
    request_data: Dict[str, Any],
) -> None:
    """
    Dispatch invitation notifications to an array of matched donor user profiles.
    """
    if not user_ids:
        return

    emergency = request_data.get("emergency_level", "normal").upper()
    blood_group = request_data.get("blood_group", "")
    hospital = request_data.get("hospital_name", "")
    req_id = request_data.get("id")

    title = f"[{emergency} REQUEST] {blood_group} Blood Needed"
    message = (
        f"A patient urgently requires {blood_group} blood at {hospital}, Peshawar. "
        f"You were identified as an eligible compatible donor. Please respond in your dashboard."
    )

    for uid in user_ids:
        try:
            await create_notification(
                user_id=uid,
                title=title,
                message=message,
                type="invitation",
                reference_type="blood_requests",
                reference_id=req_id,
            )
        except Exception as e:
            logger.warning("donor_notification_failed", user_id=uid, error=str(e))
