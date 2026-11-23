"""
Pydantic schemas for authentication endpoints.

Defines request and response models for user registration, login,
profile management, and authentication token responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: str = Field(..., pattern=EMAIL_PATTERN, description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number")
    role: str = Field(..., pattern="^(donor|patient|blood_bank)$", description="User role (donor, patient, or blood_bank)")
    blood_group: Optional[str] = Field(
        None,
        pattern=r"^(A|B|AB|O)[+-]$",
        description="Blood group for donors (e.g. A+, B-, O+, etc.)",
    )
    city: str = Field(default="Peshawar", max_length=50, description="City name")
    area: str = Field(..., max_length=100, description="Area/locality within the city")

    @model_validator(mode="after")
    def validate_donor_blood_group(self) -> "RegisterRequest":
        """Ensure donors must supply a valid blood group, while keeping it optional for patients."""
        if self.role == "donor" and not self.blood_group:
            raise ValueError("Blood group is required for donor registration")
        return self


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: str = Field(..., pattern=EMAIL_PATTERN, description="Registered email address")
    password: str = Field(..., description="Account password")


class UserProfile(BaseModel):
    """Schema for user profile data returned in responses."""

    id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field(..., description="User role (donor, patient, blood_bank, admin)")
    city: Optional[str] = Field(None, description="City")
    area: Optional[str] = Field(None, description="Area/locality")
    avatar_url: Optional[str] = Field(None, description="Profile avatar URL")
    is_verified: bool = Field(default=False, description="Whether user is verified")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Schema for authentication response containing token and user profile."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserProfile = Field(..., description="User profile data")


class ProfileUpdateRequest(BaseModel):
    """Schema for updating user profile."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Updated full name")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Updated phone number")
    city: Optional[str] = Field(None, max_length=50, description="Updated city")
    area: Optional[str] = Field(None, max_length=100, description="Updated area")
    avatar_url: Optional[str] = Field(None, description="Updated avatar URL")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: str = Field(..., pattern=EMAIL_PATTERN, description="Email address for password reset")


class MessageResponse(BaseModel):
    """Generic message response schema."""

    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Whether the operation was successful")
