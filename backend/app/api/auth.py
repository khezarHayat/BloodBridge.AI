"""
Authentication and user profile endpoints.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request

from app.core.logging import get_logger
from app.core.security import get_current_user, limiter
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    PasswordResetRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    UserProfile,
)
from app.services.auth_service import (
    get_user_profile,
    login_user,
    register_user,
    request_password_reset,
    update_user_profile,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=201)
@limiter.limit("20/minute")
async def register(request: Request, body: RegisterRequest) -> Dict[str, Any]:
    """Register a new user profile with role-based routing (donor, patient, blood_bank)."""
    return await register_user(body)


@router.post("/login", response_model=AuthResponse)
@limiter.limit("30/minute")
async def login(request: Request, body: LoginRequest) -> Dict[str, Any]:
    """Authenticate with email and password via Supabase Auth."""
    return await login_user(body)


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Logout current user session."""
    return {"message": "Logged out successfully", "success": True}


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Retrieve current authenticated user profile."""
    return await get_user_profile(current_user["id"])


@router.put("/me", response_model=UserProfile)
async def update_me(
    body: ProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update current authenticated user profile."""
    return await update_user_profile(current_user["id"], body)


@router.post("/password-reset", response_model=MessageResponse)
@limiter.limit("5/minute")
async def password_reset(request: Request, body: PasswordResetRequest) -> Dict[str, Any]:
    """Request a password reset link."""
    return await request_password_reset(body.email)
