"""
Pydantic schemas for notification endpoints.

Defines response models for user notifications including
read status management and unread counts.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Schema for notification data in API responses."""

    id: str = Field(..., description="Notification ID")
    user_id: str = Field(..., description="Recipient user ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message body")
    type: str = Field(
        ...,
        description="Notification type (invitation, request_update, system, verification, reminder)",
    )
    is_read: bool = Field(default=False, description="Whether notification has been read")
    reference_type: Optional[str] = Field(
        None,
        description="Type of referenced entity (blood_request, invitation, donor, blood_bank)",
    )
    reference_id: Optional[str] = Field(None, description="ID of referenced entity")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Paginated list of notifications."""

    notifications: List[NotificationResponse] = Field(
        default_factory=list, description="List of notifications"
    )
    total: int = Field(default=0, description="Total matching notifications")
    page: int = Field(default=1, description="Current page")
    limit: int = Field(default=20, description="Items per page")
    has_more: bool = Field(default=False, description="Whether more pages exist")
    unread_count: int = Field(default=0, description="Total unread notifications")


class UnreadCountResponse(BaseModel):
    """Response containing the count of unread notifications."""

    unread_count: int = Field(default=0, description="Number of unread notifications")
