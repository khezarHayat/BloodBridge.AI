"""
Main donor-request matching engine.

Orchestrates the full matching process: fetching compatible donors,
calculating scores, creating invitations, and sending notifications.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.supabase_client import get_supabase_admin
from app.matching.compatibility import get_compatible_donor_groups
from app.matching.geo import safe_distance
from app.matching.scoring import calculate_match_score

logger = get_logger(__name__)


class MatchResult:
    """Represents a single donor-request match result."""

    def __init__(
        self,
        donor_id: str,
        user_id: str,
        score: float,
        reasons: List[str],
        distance_km: Optional[float],
        donor_data: Dict[str, Any],
    ):
        self.donor_id = donor_id
        self.user_id = user_id
        self.score = score
        self.reasons = reasons
        self.distance_km = distance_km
        self.donor_data = donor_data

    def to_dict(self) -> Dict[str, Any]:
        """Convert match result to a dictionary."""
        return {
            "donor_id": self.donor_id,
            "user_id": self.user_id,
            "score": self.score,
            "reasons": self.reasons,
            "distance_km": self.distance_km,
        }


async def find_matching_donors(request_id: str) -> List[MatchResult]:
    """
    Find and score matching donors for a blood request.

    This is the main matching engine function that:
    1. Fetches the blood request details
    2. Determines compatible blood groups
    3. Queries eligible donors (compatible, same city, available, verified, eligible)
    4. Filters donors based on minimum donation interval (56 days)
    5. Calculates distance using Haversine formula
    6. Scores each donor
    7. Sorts by score descending
    8. Returns top N results (configurable)
    9. Creates donor_invitations records
    10. Sends notifications to matched donors
    11. Updates request status to 'matching' then 'matched'

    Args:
        request_id: The UUID of the blood request to match.

    Returns:
        List of MatchResult objects sorted by score descending.
    """
    settings = get_settings()
    supabase = get_supabase_admin()

    # Step 1: Fetch the blood request
    logger.info("matching_started", request_id=request_id)

    request_result = (
        supabase.table("blood_requests")
        .select("*")
        .eq("id", request_id)
        .maybe_single()
        .execute()
    )

    if not request_result or not request_result.data:
        logger.error("matching_request_not_found", request_id=request_id)
        return []

    blood_request = request_result.data

    # Update request status to 'matching'
    supabase.table("blood_requests").update({"status": "matching"}).eq("id", request_id).execute()

    # Step 2: Get compatible blood groups
    recipient_group = blood_request.get("blood_group", "")
    compatible_groups = get_compatible_donor_groups(recipient_group)

    if not compatible_groups:
        logger.warning("no_compatible_groups", blood_group=recipient_group)
        supabase.table("blood_requests").update({"status": "open"}).eq("id", request_id).execute()
        return []

    logger.info(
        "compatible_groups_found",
        recipient_group=recipient_group,
        compatible_groups=compatible_groups,
    )

    # Step 3: Query eligible donors
    request_city = blood_request.get("city", "Peshawar")

    query = (
        supabase.table("donors")
        .select("*, profiles!donors_user_id_fkey!inner(full_name, city, area, phone, is_verified, latitude, longitude)")
        .in_("blood_group", compatible_groups)
        .eq("profiles.city", request_city)
        .eq("is_available", True)
    )

    donors_result = query.execute()

    if not donors_result or not donors_result.data:
        logger.info("no_eligible_donors_found", request_id=request_id)
        supabase.table("blood_requests").update({"status": "open"}).eq("id", request_id).execute()
        return []

    donors = donors_result.data

    # Step 4: Filter by donation eligibility (56-day minimum interval)
    min_interval_days = settings.MIN_DONATION_INTERVAL_DAYS
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=min_interval_days)

    eligible_donors = []
    for donor in donors:
        last_donation = donor.get("last_donation_date")
        if last_donation:
            try:
                if isinstance(last_donation, str):
                    last_date = datetime.fromisoformat(last_donation.replace("Z", "+00:00"))
                else:
                    last_date = last_donation
                if last_date.tzinfo is None:
                    last_date = last_date.replace(tzinfo=timezone.utc)
                if last_date > cutoff_date:
                    continue  # Not eligible yet
            except (ValueError, TypeError):
                pass  # If parsing fails, consider the donor eligible
        eligible_donors.append(donor)

    logger.info(
        "eligible_donors_filtered",
        total_queried=len(donors),
        eligible_count=len(eligible_donors),
        min_interval_days=min_interval_days,
    )

    # Step 5 & 6: Calculate distance and score each donor
    match_results: List[MatchResult] = []

    for donor in eligible_donors:
        profile = donor.get("profiles", {})
        if isinstance(profile, list) and profile:
            profile = profile[0]
        elif isinstance(profile, list):
            profile = {}

        # Build flat donor data for scoring
        donor_data = {
            "id": donor.get("id"),
            "user_id": donor.get("user_id"),
            "blood_group": donor.get("blood_group"),
            "is_available": donor.get("is_available", False),
            "total_donations": donor.get("total_donations", 0),
            "is_verified": profile.get("is_verified", False),
            "area": profile.get("area", donor.get("area", "")),
            "city": profile.get("city", ""),
            "latitude": profile.get("latitude"),
            "longitude": profile.get("longitude"),
            "full_name": profile.get("full_name", ""),
        }

        # Calculate distance
        distance_km = safe_distance(
            donor_data.get("latitude"),
            donor_data.get("longitude"),
            blood_request.get("latitude"),
            blood_request.get("longitude"),
        )

        # Calculate match score
        score, reasons = calculate_match_score(donor_data, blood_request, distance_km)

        match_results.append(
            MatchResult(
                donor_id=donor.get("id", ""),
                user_id=donor.get("user_id", ""),
                score=score,
                reasons=reasons,
                distance_km=round(distance_km, 2) if distance_km is not None else None,
                donor_data=donor_data,
            )
        )

    # Step 7: Sort by score descending
    match_results.sort(key=lambda m: m.score, reverse=True)

    # Step 8: Limit to top N results
    max_results = settings.MAX_MATCH_RESULTS
    top_matches = match_results[:max_results]

    logger.info(
        "matching_scored",
        total_matches=len(match_results),
        top_matches=len(top_matches),
        top_score=top_matches[0].score if top_matches else 0,
    )

    # Step 9: Create donor_invitations records
    await _create_invitations(request_id, top_matches, supabase)

    # Step 10: Send notifications to matched donors
    await _notify_matched_donors(top_matches, blood_request)

    # Step 11: Update request status to 'matched'
    matched_count = len(top_matches)
    new_status = "matched" if matched_count > 0 else "open"
    supabase.table("blood_requests").update(
        {
            "status": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", request_id).execute()

    logger.info(
        "matching_completed",
        request_id=request_id,
        matched_count=matched_count,
        final_status=new_status,
    )

    return top_matches


async def _create_invitations(
    request_id: str,
    matches: List[MatchResult],
    supabase,
) -> None:
    """
    Create donor invitation records for matched donors.

    Checks for existing invitations to avoid duplicates.

    Args:
        request_id: The blood request ID.
        matches: List of match results.
        supabase: Supabase admin client.
    """
    if not matches:
        return

    # Check for existing invitations to avoid duplicates
    donor_ids = [m.donor_id for m in matches]
    existing_result = (
        supabase.table("donor_invitations")
        .select("donor_id")
        .eq("request_id", request_id)
        .in_("donor_id", donor_ids)
        .execute()
    )

    existing_donor_ids = set()
    if existing_result and existing_result.data:
        existing_donor_ids = {inv["donor_id"] for inv in existing_result.data}

    # Create new invitations
    invitations = []
    now = datetime.now(timezone.utc).isoformat()

    for match in matches:
        if match.donor_id in existing_donor_ids:
            logger.info(
                "invitation_already_exists",
                request_id=request_id,
                donor_id=match.donor_id,
            )
            continue

        invitations.append(
            {
                "request_id": request_id,
                "donor_id": match.donor_id,
                "status": "pending",
                "match_score": match.score,
                "match_reasons": match.reasons,
                "distance_km": match.distance_km,
                "invited_at": now,
            }
        )

    if invitations:
        try:
            supabase.table("donor_invitations").insert(invitations).execute()
            logger.info(
                "invitations_created",
                request_id=request_id,
                count=len(invitations),
            )
        except Exception as e:
            logger.error(
                "invitation_creation_failed",
                request_id=request_id,
                error=str(e),
            )


async def _notify_matched_donors(
    matches: List[MatchResult],
    blood_request: Dict[str, Any],
) -> None:
    """
    Send notifications to matched donors about a blood request.

    Args:
        matches: List of match results.
        blood_request: The blood request data.
    """
    supabase = get_supabase_admin()

    patient_name = blood_request.get("patient_name", "A patient")
    blood_group = blood_request.get("blood_group", "")
    hospital = blood_request.get("hospital_name", "")
    emergency = blood_request.get("emergency_level", "normal")
    request_id = blood_request.get("id", "")

    emergency_prefix = ""
    if emergency == "critical":
        emergency_prefix = "🚨 CRITICAL: "
    elif emergency == "urgent":
        emergency_prefix = "⚠️ URGENT: "

    notifications = []
    now = datetime.now(timezone.utc).isoformat()

    for match in matches:
        notifications.append(
            {
                "user_id": match.user_id,
                "title": f"{emergency_prefix}Blood Donation Request",
                "message": (
                    f"{patient_name} needs {blood_group} blood at {hospital}. "
                    f"You've been matched as a compatible donor"
                    f"{f' ({match.distance_km:.1f} km away)' if match.distance_km else ''}. "
                    f"Please check your invitations to respond."
                ),
                "type": "invitation",
                "reference_type": "blood_request",
                "reference_id": request_id,
                "is_read": False,
                "created_at": now,
            }
        )

    if notifications:
        try:
            supabase.table("notifications").insert(notifications).execute()
            logger.info(
                "donor_notifications_sent",
                request_id=request_id,
                count=len(notifications),
            )
        except Exception as e:
            logger.error(
                "donor_notification_failed",
                request_id=request_id,
                error=str(e),
            )
