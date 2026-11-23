"""
Pydantic schemas for blood bank endpoints.

Defines request and response models for blood bank registration,
inventory management, and inventory reporting.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class BloodBankCreate(BaseModel):
    """Schema for registering a new blood bank."""

    name: str = Field(..., min_length=2, max_length=200, description="Blood bank name")
    license_number: str = Field(..., min_length=3, max_length=50, description="License number")
    type: str = Field(
        default="hospital",
        pattern="^(government|private|hospital|ngo)$",
        description="Blood bank type",
    )
    phone: str = Field(..., min_length=10, max_length=15, description="Contact phone")
    email: Optional[str] = Field(None, pattern=EMAIL_PATTERN, description="Contact email")
    address: str = Field(..., min_length=5, max_length=300, description="Full address")
    city: str = Field(default="Peshawar", max_length=50, description="City")
    area: str = Field(..., max_length=100, description="Area/locality")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    operating_hours: Optional[str] = Field(
        None, max_length=200, description="Operating hours (e.g., '9 AM - 5 PM')"
    )


class BloodBankUpdate(BaseModel):
    """Schema for updating blood bank information."""

    name: Optional[str] = Field(None, min_length=2, max_length=200, description="Updated name")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Updated phone")
    email: Optional[str] = Field(None, pattern=EMAIL_PATTERN, description="Updated email")
    address: Optional[str] = Field(None, min_length=5, max_length=300, description="Updated address")
    area: Optional[str] = Field(None, max_length=100, description="Updated area")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Updated latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Updated longitude")
    operating_hours: Optional[str] = Field(None, max_length=200, description="Updated hours")


class BloodBankResponse(BaseModel):
    """Schema for blood bank data in API responses."""

    id: str = Field(..., description="Blood bank ID")
    user_id: str = Field(..., description="Owner user ID")
    name: str = Field(..., description="Blood bank name")
    license_number: str = Field(..., description="License number")
    type: str = Field(..., description="Blood bank type")
    phone: str = Field(..., description="Contact phone")
    email: Optional[str] = Field(None, description="Contact email")
    address: str = Field(..., description="Full address")
    city: str = Field(..., description="City")
    area: str = Field(..., description="Area")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    operating_hours: Optional[str] = Field(None, description="Operating hours")
    is_verified: bool = Field(default=False, description="Verification status")
    created_at: Optional[datetime] = Field(None, description="Registration date")

    model_config = {"from_attributes": True}


class BloodBankListResponse(BaseModel):
    """Paginated list of blood banks."""

    blood_banks: List[BloodBankResponse] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    limit: int = Field(default=20)
    has_more: bool = Field(default=False)


class InventoryBatchCreate(BaseModel):
    """Schema for adding a new inventory batch to a blood bank."""

    blood_group: str = Field(
        ...,
        pattern="^(A|B|AB|O)[+-]$",
        description="Blood group of this batch",
    )
    units_available: int = Field(..., ge=1, le=1000, description="Number of available units")
    collection_date: date = Field(..., description="Date blood was collected")
    expiry_date: date = Field(..., description="Expiry date of the blood units")
    screening_status: str = Field(
        default="pending",
        pattern="^(pending|cleared|rejected|quarantined)$",
        description="Screening status",
    )
    batch_number: Optional[str] = Field(None, max_length=50, description="Internal batch number")


class InventoryBatchUpdate(BaseModel):
    """Schema for updating an inventory batch."""

    units_available: Optional[int] = Field(None, ge=0, le=1000, description="Updated available units")
    screening_status: Optional[str] = Field(
        None,
        pattern="^(pending|cleared|rejected|quarantined)$",
        description="Updated screening status",
    )
    batch_number: Optional[str] = Field(None, max_length=50, description="Updated batch number")


class InventoryBatchResponse(BaseModel):
    """Schema for inventory batch data in API responses."""

    id: str = Field(..., description="Batch ID")
    blood_bank_id: str = Field(..., description="Blood bank ID")
    blood_group: str = Field(..., description="Blood group")
    units_available: int = Field(..., description="Available units")
    collection_date: date = Field(..., description="Collection date")
    expiry_date: date = Field(..., description="Expiry date")
    screening_status: str = Field(..., description="Screening status")
    batch_number: Optional[str] = Field(None, description="Batch number")
    is_expired: bool = Field(default=False, description="Whether batch is expired")
    created_at: Optional[datetime] = Field(None, description="Record creation date")

    model_config = {"from_attributes": True}


class InventoryBatchListResponse(BaseModel):
    """Paginated list of inventory batches."""

    batches: List[InventoryBatchResponse] = Field(default_factory=list)
    items: List[InventoryBatchResponse] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    limit: int = Field(default=20)
    has_more: bool = Field(default=False)


class InventorySummary(BaseModel):
    """Summary of inventory for a specific blood group."""

    blood_group: str = Field(..., description="Blood group")
    total_units: int = Field(default=0, description="Total units including all statuses")
    available_units: int = Field(default=0, description="Units that are cleared and not expired")
    pending_units: int = Field(default=0, description="Units pending screening")
    expired_units: int = Field(default=0, description="Expired units")


class InventorySummaryResponse(BaseModel):
    """Full inventory summary for a blood bank."""

    blood_bank_id: str = Field(..., description="Blood bank ID")
    blood_bank_name: str = Field(..., description="Blood bank name")
    summary: List[InventorySummary] = Field(default_factory=list, description="Per blood group summary")
    total_available: int = Field(default=0, description="Total available units across all groups")
    last_updated: Optional[datetime] = Field(None, description="Last inventory update time")
