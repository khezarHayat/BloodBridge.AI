"""
Donor-request match scoring system.

Provides a configurable scoring system that evaluates how well a donor
matches a blood donation request based on multiple factors including
blood group compatibility, location, availability, and verification status.
"""

from typing import Any, Dict, List, Optional, Tuple

from app.matching.compatibility import is_compatible, is_exact_match
from app.matching.geo import calculate_distance_score, safe_distance


# Scoring weights (configurable)
EXACT_BLOOD_GROUP_MATCH: float = 30.0
COMPATIBLE_BLOOD_GROUP: float = 15.0
SAME_AREA: float = 25.0
DISTANCE_SCORE_MAX: float = 20.0
AVAILABILITY_SCORE: float = 10.0
RECENT_ACTIVITY: float = 5.0
VERIFICATION_BONUS: float = 10.0
CRITICAL_EMERGENCY_BOOST: float = 15.0
URGENT_EMERGENCY_BOOST: float = 8.0

# Maximum possible score for normalization reference
MAX_POSSIBLE_SCORE: float = (
    EXACT_BLOOD_GROUP_MATCH
    + SAME_AREA
    + DISTANCE_SCORE_MAX
    + AVAILABILITY_SCORE
    + RECENT_ACTIVITY
    + VERIFICATION_BONUS
    + CRITICAL_EMERGENCY_BOOST
)


def calculate_match_score(
    donor: Dict[str, Any],
    request: Dict[str, Any],
    distance_km: Optional[float] = None,
) -> Tuple[float, List[str]]:
    """
    Calculate a match score between a donor and a blood request.

    Evaluates multiple factors and returns both a numeric score and
    a human-readable list of reasons that contributed to the score.

    Scoring breakdown:
        - Exact blood group match: 30 points
        - Compatible blood group (non-exact): 15 points
        - Same area/locality: 25 points
        - Distance score: up to 20 points (closer = higher)
        - Availability: 10 points
        - Recent activity: 5 points
        - Verified donor: 10 points
        - Critical emergency boost: 15 points
        - Urgent emergency boost: 8 points

    Args:
        donor: Donor record dictionary with fields like blood_group, area, city,
               is_available, is_verified, latitude, longitude, total_donations.
        request: Blood request record dictionary with fields like blood_group,
                 area, city, emergency_level, latitude, longitude.
        distance_km: Pre-calculated distance in km (if available).

    Returns:
        Tuple of (score, reasons) where score is a float and reasons is a list
        of human-readable strings explaining the score components.
    """
    score = 0.0
    reasons: List[str] = []

    donor_blood_group = donor.get("blood_group", "")
    request_blood_group = request.get("blood_group", "")

    # Blood group compatibility scoring
    if is_exact_match(donor_blood_group, request_blood_group):
        score += EXACT_BLOOD_GROUP_MATCH
        reasons.append(f"Exact blood group match ({donor_blood_group}): +{EXACT_BLOOD_GROUP_MATCH}")
    elif is_compatible(donor_blood_group, request_blood_group):
        score += COMPATIBLE_BLOOD_GROUP
        reasons.append(
            f"Compatible blood group ({donor_blood_group} → {request_blood_group}): "
            f"+{COMPATIBLE_BLOOD_GROUP}"
        )

    # Location scoring - same area
    donor_area = (donor.get("area") or "").lower().strip()
    request_area = (request.get("area") or "").lower().strip()
    if donor_area and request_area and donor_area == request_area:
        score += SAME_AREA
        reasons.append(f"Same area ({donor.get('area')}): +{SAME_AREA}")

    # Distance-based scoring
    if distance_km is None:
        distance_km = safe_distance(
            donor.get("latitude"),
            donor.get("longitude"),
            request.get("latitude"),
            request.get("longitude"),
        )

    if distance_km is not None:
        dist_score = calculate_distance_score(distance_km)
        if dist_score > 0:
            score += dist_score
            reasons.append(f"Proximity ({distance_km:.1f} km): +{dist_score:.1f}")

    # Availability scoring
    if donor.get("is_available", False):
        score += AVAILABILITY_SCORE
        reasons.append(f"Currently available: +{AVAILABILITY_SCORE}")

    # Recent activity scoring (active donor with past donations)
    total_donations = donor.get("total_donations", 0)
    if total_donations and total_donations > 0:
        score += RECENT_ACTIVITY
        reasons.append(f"Active donor ({total_donations} donations): +{RECENT_ACTIVITY}")

    # Verification bonus
    if donor.get("is_verified", False):
        score += VERIFICATION_BONUS
        reasons.append(f"Verified donor: +{VERIFICATION_BONUS}")

    # Emergency level boost
    emergency_level = request.get("emergency_level", "normal")
    if emergency_level == "critical":
        score += CRITICAL_EMERGENCY_BOOST
        reasons.append(f"Critical emergency boost: +{CRITICAL_EMERGENCY_BOOST}")
    elif emergency_level == "urgent":
        score += URGENT_EMERGENCY_BOOST
        reasons.append(f"Urgent emergency boost: +{URGENT_EMERGENCY_BOOST}")

    return round(score, 2), reasons
