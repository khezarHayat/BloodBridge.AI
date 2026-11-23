"""
Pydantic schemas for donor invitation endpoints.

Defines response and action models for managing invitations
sent to donors for blood donation requests.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class InvitationResponse(BaseModel):
    """Schema for donor invitation data in API responses."""

    id: str = Field(..., description="Invitation ID")
    request_id: str = Field(..., description="Associated blood request ID")
    donor_id: str = Field(..., description="Invited donor ID")
    status: str = Field(
        default="pending",
        description="Invitation status (pending, accepted, declined, expired)",
    )
    match_score: float = Field(default=0.0, description="Computed match score")
    match_reasons: Optional[List[str]] = Field(
        None, description="List of reasons contributing to match score"
    )
    distance_km: Optional[float] = Field(None, description="Distance from donor to hospital in km")
    invited_at: Optional[datetime] = Field(None, description="Invitation timestamp")
    responded_at: Optional[datetime] = Field(None, description="Response timestamp")
    response_notes: Optional[str] = Field(None, description="Donor's response notes")

    # Request details for context
    patient_name: Optional[str] = Field(None, description="Patient name from the request")
    blood_group: Optional[str] = Field(None, description="Required blood group")
    hospital_name: Optional[str] = Field(None, description="Hospital name")
    emergency_level: Optional[str] = Field(None, description="Emergency level")

    model_config = {"from_attributes": True}


class InvitationListResponse(BaseModel):
    """List of donor invitations."""

    invitations: List[InvitationResponse] = Field(
        default_factory=list, description="List of invitations"
    )
    total: int = Field(default=0, description="Total invitations")


class InvitationAction(BaseModel):
    """Schema for accepting or declining an invitation."""

    status: str = Field(
        ...,
        pattern="^(accepted|declined)$",
        description="Action: 'accepted' or 'declined'",
    )
    response_notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes from the donor"
    )
