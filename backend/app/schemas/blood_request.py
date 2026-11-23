"""
Pydantic schemas for blood request endpoints.

Defines request and response models for creating, updating, listing,
and managing blood donation requests.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BloodRequestCreate(BaseModel):
    """Schema for creating a new blood donation request."""

    patient_name: str = Field(..., min_length=2, max_length=100, description="Patient's full name")
    blood_group: str = Field(
        ...,
        pattern="^(A|B|AB|O)[+-]$",
        description="Required blood group",
    )
    units_needed: int = Field(..., ge=1, le=20, description="Number of blood units needed")
    hospital_name: str = Field(..., min_length=2, max_length=200, description="Hospital name")
    hospital_address: str = Field(..., min_length=5, max_length=300, description="Hospital address")
    city: str = Field(default="Peshawar", max_length=50, description="City")
    area: str = Field(..., max_length=100, description="Area/locality")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Hospital latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Hospital longitude")
    emergency_level: str = Field(
        default="normal",
        pattern="^(critical|urgent|normal)$",
        description="Emergency level",
    )
    required_by: Optional[datetime] = Field(None, description="Deadline for the blood requirement")
    contact_name: str = Field(..., min_length=2, max_length=100, description="Contact person's name")
    contact_phone: str = Field(..., min_length=10, max_length=15, description="Contact phone number")
    additional_notes: Optional[str] = Field(
        None, max_length=1000, description="Additional notes or requirements"
    )


class BloodRequestUpdate(BaseModel):
    """Schema for updating a blood request."""

    status: Optional[str] = Field(
        None,
        pattern="^(pending|open|matching|matched|donor_confirmed|partially_fulfilled|fulfilled|cancelled|expired)$",
        description="Updated request status",
    )
    units_fulfilled: Optional[int] = Field(None, ge=0, description="Number of units fulfilled so far")
    cancellation_reason: Optional[str] = Field(
        None, max_length=500, description="Reason for cancellation"
    )
    additional_notes: Optional[str] = Field(
        None, max_length=1000, description="Updated notes"
    )


class BloodRequestResponse(BaseModel):
    """Schema for blood request data in API responses."""

    id: str = Field(..., description="Blood request ID")
    request_number: Optional[str] = Field(None, description="Formatted request number")
    requester_id: str = Field(..., description="ID of the user who created the request")
    requester_name: Optional[str] = Field(None, description="Name of the requester")
    patient_name: str = Field(..., description="Patient name")
    blood_group: str = Field(..., description="Required blood group")
    units_needed: int = Field(..., description="Units needed")
    units_fulfilled: int = Field(default=0, description="Units fulfilled")
    hospital_name: str = Field(..., description="Hospital name")
    hospital_address: str = Field(..., description="Hospital address")
    city: str = Field(..., description="City")
    area: str = Field(..., description="Area")
    latitude: Optional[float] = Field(None, description="Hospital latitude")
    longitude: Optional[float] = Field(None, description="Hospital longitude")
    emergency_level: str = Field(default="normal", description="Emergency level")
    status: str = Field(default="open", description="Request status")
    required_by: Optional[datetime] = Field(None, description="Deadline")
    contact_name: str = Field(..., description="Contact name")
    contact_phone: str = Field(..., description="Contact phone")
    additional_notes: Optional[str] = Field(None, description="Additional notes")
    matched_donors: int = Field(default=0, description="Number of matched donors")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class BloodRequestListResponse(BaseModel):
    """Paginated list of blood requests."""

    requests: List[BloodRequestResponse] = Field(
        default_factory=list, description="List of blood requests"
    )
    total: int = Field(default=0, description="Total matching requests")
    page: int = Field(default=1, description="Current page")
    limit: int = Field(default=20, description="Items per page")
    has_more: bool = Field(default=False, description="Whether more pages exist")
