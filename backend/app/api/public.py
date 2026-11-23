"""
Public discovery and informational endpoints.
"""

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.supabase_client import get_supabase_admin
from app.matching.compatibility import COMPATIBILITY_MAP

EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

router = APIRouter(prefix="/api/public", tags=["Public Discovery"])


class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=EMAIL_PATTERN)
    phone: str = Field(..., min_length=10, max_length=15)
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)


PESHAWAR_AREAS = [
    {"name": "Hayatabad", "district": "Peshawar", "lat": 34.0017, "lng": 71.4448, "zip": "25000"},
    {"name": "University Town", "district": "Peshawar", "lat": 34.0085, "lng": 71.4785, "zip": "25000"},
    {"name": "Saddar", "district": "Peshawar", "lat": 34.0253, "lng": 71.5784, "zip": "25000"},
    {"name": "Gulbahar", "district": "Peshawar", "lat": 34.0312, "lng": 71.5656, "zip": "25000"},
    {"name": "Warsak Road", "district": "Peshawar", "lat": 34.0620, "lng": 71.5120, "zip": "25000"},
    {"name": "Ring Road", "district": "Peshawar", "lat": 33.9850, "lng": 71.5540, "zip": "25000"},
    {"name": "Kohat Road", "district": "Peshawar", "lat": 33.9520, "lng": 71.5410, "zip": "25000"},
    {"name": "Dalazak Road", "district": "Peshawar", "lat": 34.0410, "lng": 71.6020, "zip": "25000"},
    {"name": "Dabgari Gardens", "district": "Peshawar", "lat": 34.0080, "lng": 71.5620, "zip": "25000"},
    {"name": "Charsadda Road", "district": "Peshawar", "lat": 34.0550, "lng": 71.5830, "zip": "25000"},
]


@router.get("/stats")
async def get_public_stats() -> Dict[str, Any]:
    """Retrieve public platform metrics for the landing page."""
    supabase = get_supabase_admin()

    d_res = supabase.table("donors").select("id", count="exact").execute()
    total_donors = d_res.count or 0

    f_res = supabase.table("blood_requests").select("id", count="exact").eq("status", "fulfilled").execute()
    fulfilled_requests = f_res.count or 0

    b_res = supabase.table("blood_banks").select("id", count="exact").eq("is_verified", True).execute()
    verified_banks = b_res.count or 0

    a_res = (
        supabase.table("blood_requests")
        .select("id", count="exact")
        .in_("status", ["pending", "matching", "matched"])
        .execute()
    )
    active_requests = a_res.count or 0

    return {
        "registered_donors": total_donors,
        "lives_impacted": fulfilled_requests * 3,  # 1 unit saves up to 3 lives
        "fulfilled_requests": fulfilled_requests,
        "verified_blood_banks": verified_banks,
        "active_emergency_requests": active_requests,
        "district": "Peshawar",
    }


@router.get("/blood-groups")
async def get_blood_groups_info() -> Dict[str, Any]:
    """Provide blood group compatibility matrix and clinical facts."""
    return {
        "compatibility": COMPATIBILITY_MAP,
        "universal_donor": "O-",
        "universal_recipient": "AB+",
        "disclaimer": "Automated matching identifies potential compatibility. Clinical cross-matching must be verified by a certified laboratory technician prior to transfusion.",
    }


@router.get("/areas")
async def get_supported_areas() -> List[Dict[str, Any]]:
    """Return supported Peshawar metropolitan locations with approximate geo-coordinates."""
    return PESHAWAR_AREAS


@router.post("/contact")
async def submit_contact(body: ContactMessage) -> Dict[str, Any]:
    """Receive community and institutional inquiries."""
    return {
        "success": True,
        "message": "Thank you for reaching out to BloodBridge Peshawar. Our medical coordination team will contact you shortly.",
    }
