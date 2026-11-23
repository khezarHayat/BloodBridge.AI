"""
Pydantic schemas for donor-related endpoints.

Defines request and response models for donor profile creation,
updates, listing, and donor invitation management.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DonorCreate(BaseModel):
    """Schema for creating a new donor profile."""

    blood_group: str = Field(
        ...,
        pattern="^(A|B|AB|O)[+-]$",
        description="Blood group (e.g., A+, B-, AB+, O-)",
    )
    date_of_birth: date = Field(..., description="Date of birth")
    gender: str = Field(
        ...,
        pattern="^(male|female|other)$",
        description="Gender (male, female, other)",
    )
    weight: float = Field(..., gt=40, lt=200, description="Weight in kg (must be > 40)")
    last_donation_date: Optional[date] = Field(
        None, description="Date of last blood donation"
    )
    consent_notifications: bool = Field(
        default=True, description="Consent to receive donation request notifications"
    )
    medical_conditions: Optional[str] = Field(
        None, max_length=500, description="Known medical conditions"
    )


class DonorUpdate(BaseModel):
    """Schema for updating donor profile fields."""

    is_available: Optional[bool] = Field(None, description="Toggle availability status")
    availability_radius_km: Optional[float] = Field(
        None, ge=1, le=100, description="Availability radius in km"
    )
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Updated phone")
    area: Optional[str] = Field(None, max_length=100, description="Updated area/locality")
    last_donation_date: Optional[date] = Field(None, description="Update last donation date")
    weight: Optional[float] = Field(None, gt=40, lt=200, description="Updated weight in kg")
    consent_notifications: Optional[bool] = Field(
        None, description="Update notification consent"
    )
    medical_conditions: Optional[str] = Field(
        None, max_length=500, description="Updated medical conditions"
    )


class DonorResponse(BaseModel):
    """Schema for donor data in API responses."""

    id: str = Field(..., description="Donor record ID")
    user_id: str = Field(..., description="Associated user/profile ID")
    full_name: str = Field(..., description="Donor's full name")
    blood_group: str = Field(..., description="Blood group")
    is_available: bool = Field(default=True, description="Whether donor is currently available")
    area: Optional[str] = Field(None, description="Area/locality")
    city: Optional[str] = Field(None, description="City")
    distance_km: Optional[float] = Field(None, description="Distance from requester in km")
    last_donation_date: Optional[date] = Field(None, description="Date of last donation")
    total_donations: int = Field(default=0, description="Total number of donations")
    is_verified: bool = Field(default=False, description="Whether donor is verified")
    gender: Optional[str] = Field(None, description="Gender")
    created_at: Optional[datetime] = Field(None, description="Profile creation date")

    model_config = {"from_attributes": True}


class DonorListResponse(BaseModel):
    """Paginated list of donors."""

    donors: List[DonorResponse] = Field(default_factory=list, description="List of donors")
    total: int = Field(default=0, description="Total number of matching donors")
    page: int = Field(default=1, description="Current page number")
    limit: int = Field(default=20, description="Items per page")
    has_more: bool = Field(default=False, description="Whether more pages are available")


class DonorAvailabilityToggle(BaseModel):
    """Schema for toggling donor availability."""

    is_available: bool = Field(..., description="New availability status")
