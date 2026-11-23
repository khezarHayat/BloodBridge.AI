"""
Unit tests for the BloodBridge intelligent matching engine.
Tests blood group compatibility, scoring algorithm, and distance calculations.
"""

from datetime import date, datetime, timedelta, timezone
import pytest

from app.matching.compatibility import (
    COMPATIBILITY_MAP,
    get_compatible_donor_groups,
    is_compatible,
)
from app.matching.geo import haversine_distance, is_within_radius, safe_distance
from app.matching.scoring import calculate_match_score


def test_compatibility_universal_donor():
    """O- blood is the universal red blood cell donor."""
    for recipient in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
        assert is_compatible("O-", recipient) is True, f"O- should be compatible with {recipient}"


def test_compatibility_universal_recipient():
    """AB+ can receive blood from any donor group."""
    for donor in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
        assert is_compatible(donor, "AB+") is True, f"{donor} should be compatible with AB+"


def test_incompatible_groups():
    """Test standard clinical incompatibilities."""
    # A+ cannot donate to O-
    assert is_compatible("A+", "O-") is False
    # B+ cannot donate to A+
    assert is_compatible("B+", "A+") is False
    # AB+ cannot donate to B+
    assert is_compatible("AB+", "B+") is False
    # O+ cannot donate to O-
    assert is_compatible("O+", "O-") is False


def test_get_compatible_donor_groups():
    """Test retrieving allowed donor groups for specific recipients."""
    assert set(get_compatible_donor_groups("O-")) == {"O-"}
    assert set(get_compatible_donor_groups("O+")) == {"O+", "O-"}
    assert set(get_compatible_donor_groups("A-")) == {"A-", "O-"}
    assert set(get_compatible_donor_groups("A+")) == {"A+", "A-", "O+", "O-"}


def test_haversine_distance():
    """
    Test distance between known landmarks in Peshawar:
    Hayatabad (34.0017, 71.4448) to University Town (34.0085, 71.4785).
    Straight line distance is approximately 3.2 km.
    """
    dist = haversine_distance(34.0017, 71.4448, 34.0085, 71.4785)
    assert 2.5 <= dist <= 4.0, f"Expected approx 3.2 km, got {dist}"


def test_haversine_distance_same_point():
    """Distance between identical coordinates must be 0."""
    dist = haversine_distance(34.0017, 71.4448, 34.0017, 71.4448)
    assert dist == 0.0


def test_scoring_exact_match_same_area():
    """
    An exact blood group match in the same area for a critical emergency
    should receive a high composite match score.
    """
    donor = {
        "id": "donor-123",
        "blood_group": "B+",
        "area": "Hayatabad",
        "is_available": True,
        "is_verified": True,
        "total_donations": 3,
        "last_donation_date": (date.today() - timedelta(days=90)).isoformat(),
    }
    request = {
        "blood_group": "B+",
        "area": "Hayatabad",
        "emergency_level": "critical",
    }
    score, reasons = calculate_match_score(donor, request, distance_km=2.0)
    assert score > 75, f"Expected high score for ideal candidate, got {score}"
    assert any("Exact blood group" in r for r in reasons)
    assert any("Same area" in r or "Hayatabad" in r for r in reasons)


def test_scoring_compatible_vs_exact():
    """Exact group match should score higher than compatible match under equal conditions."""
    exact_donor = {
        "id": "d1",
        "blood_group": "A+",
        "area": "Saddar",
        "is_available": True,
        "is_verified": False,
        "total_donations": 0,
    }
    comp_donor = {
        "id": "d2",
        "blood_group": "O+",
        "area": "Saddar",
        "is_available": True,
        "is_verified": False,
        "total_donations": 0,
    }
    req = {"blood_group": "A+", "area": "Saddar", "emergency_level": "normal"}

    score_exact, _ = calculate_match_score(exact_donor, req, distance_km=5.0)
    score_comp, _ = calculate_match_score(comp_donor, req, distance_km=5.0)

    assert score_exact > score_comp
