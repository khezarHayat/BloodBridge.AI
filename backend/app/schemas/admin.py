"""
Pydantic schemas for admin dashboard and management endpoints.

Defines models for platform statistics, user management,
verification actions, audit logs, and analytics data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    """Schema for admin dashboard statistics."""

    total_users: int = Field(default=0, description="Total registered users")
    total_donors: int = Field(default=0, description="Total registered donors")
    verified_donors: int = Field(default=0, description="Verified donors count")
    active_requests: int = Field(default=0, description="Currently active blood requests")
    completed_requests: int = Field(default=0, description="Fulfilled blood requests")
    registered_blood_banks: int = Field(default=0, description="Registered blood banks")
    pending_verifications: int = Field(default=0, description="Pending verification requests")
    total_donations: int = Field(default=0, description="Total completed donations")


class UserManagementResponse(BaseModel):
    """Schema for user data in admin management views."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field(..., description="User role")
    city: Optional[str] = Field(None, description="City")
    area: Optional[str] = Field(None, description="Area")
    is_verified: bool = Field(default=False, description="Verification status")
    is_active: bool = Field(default=True, description="Active status")
    created_at: Optional[datetime] = Field(None, description="Registration date")

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Paginated list of users for admin management."""

    users: List[UserManagementResponse] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    limit: int = Field(default=20)
    has_more: bool = Field(default=False)


class VerificationAction(BaseModel):
    """Schema for admin verification/rejection action."""

    status: str = Field(
        ...,
        pattern="^(verified|rejected)$",
        description="Verification decision",
    )
    review_notes: Optional[str] = Field(
        None, max_length=500, description="Admin review notes"
    )


class DeactivateAction(BaseModel):
    """Schema for user deactivation with reason."""

    reason: Optional[str] = Field(
        None, max_length=500, description="Reason for deactivation"
    )


class AuditLogResponse(BaseModel):
    """Schema for audit log entries."""

    id: str = Field(..., description="Audit log entry ID")
    user_id: Optional[str] = Field(None, description="User who performed the action")
    user_name: Optional[str] = Field(None, description="Name of the user")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="ID of affected resource")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional action details")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    created_at: Optional[datetime] = Field(None, description="Timestamp")

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """Paginated list of audit log entries."""

    logs: List[AuditLogResponse] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    limit: int = Field(default=20)
    has_more: bool = Field(default=False)


class AnalyticsDataPoint(BaseModel):
    """Generic analytics data point."""

    label: str = Field(..., description="Category/label")
    value: int = Field(default=0, description="Count/value")
    percentage: Optional[float] = Field(None, description="Percentage of total")


class AnalyticsResponse(BaseModel):
    """Generic analytics response with data points."""

    title: str = Field(..., description="Analytics title")
    data: List[AnalyticsDataPoint] = Field(default_factory=list)
    total: int = Field(default=0, description="Total across all data points")
    period: Optional[str] = Field(None, description="Time period covered")
