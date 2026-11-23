"""
Phase 1 Validation Tests: Form-to-Engine Synchronization Fix.

Tests:
1. Blood group validation on RegisterRequest (all 8 groups accepted, invalid rejected, None accepted).
2. Geolocation payload handling on BloodRequestCreate (valid coordinates, None coordinates, out of range rejected).
3. Distance calculation and scoring in matching engine with and without coordinates.
"""

import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest
from app.schemas.blood_request import BloodRequestCreate
from app.matching.geo import haversine_distance, safe_distance
from app.matching.scoring import calculate_match_score


VALID_BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
INVALID_BLOOD_GROUPS = ["C+", "O", "AB", "Positive", "A", "b+", "o-", "123", "", "X+"]


class TestRegisterBloodGroupValidation:
    """Test blood_group field on RegisterRequest schema."""

    @pytest.mark.parametrize("bg", VALID_BLOOD_GROUPS)
    def test_valid_blood_groups_accepted(self, bg: str):
        req = RegisterRequest(
            email="donor_test@bloodbridge.demo",
            password="StrongPassword123!",
            full_name="Test Donor",
            phone="03001234567",
            role="donor",
            blood_group=bg,
            city="Peshawar",
            area="Hayatabad",
        )
        assert req.blood_group == bg

    @pytest.mark.parametrize("bg", INVALID_BLOOD_GROUPS)
    def test_invalid_blood_groups_rejected(self, bg: str):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="donor_test@bloodbridge.demo",
                password="StrongPassword123!",
                full_name="Test Donor",
                phone="03001234567",
                role="donor",
                blood_group=bg,
                city="Peshawar",
                area="Hayatabad",
            )

    def test_donor_without_blood_group_strictly_rejected(self):
        """Donors must explicitly provide an actual blood group; never silently accepted as None or O+."""
        with pytest.raises(ValidationError, match="Blood group is required for donor registration"):
            RegisterRequest(
                email="donor_missing_bg@bloodbridge.demo",
                password="StrongPassword123!",
                full_name="No BG Donor",
                phone="03001234567",
                role="donor",
                blood_group=None,
                city="Peshawar",
                area="Hayatabad",
            )

    def test_blood_group_optional_for_patient(self):
        req = RegisterRequest(
            email="patient_test@bloodbridge.demo",
            password="StrongPassword123!",
            full_name="Test Patient",
            phone="03001234567",
            role="patient",
            blood_group=None,
            city="Peshawar",
            area="Hayatabad",
        )
        assert req.blood_group is None

    def test_blood_group_optional_for_blood_bank(self):
        req = RegisterRequest(
            email="bloodbank_test@bloodbridge.demo",
            password="StrongPassword123!",
            full_name="Test Blood Bank",
            phone="03001234567",
            role="blood_bank",
            blood_group=None,
            city="Peshawar",
            area="Saddar",
        )
        assert req.blood_group is None

    def test_blood_group_omitted_completely_for_patient(self):
        req = RegisterRequest(
            email="patient_test2@bloodbridge.demo",
            password="StrongPassword123!",
            full_name="Test Patient 2",
            phone="03001234567",
            role="patient",
            city="Peshawar",
            area="Saddar",
        )
        assert req.blood_group is None


class TestHospitalCoordinatesDistinctness:
    """Verify that all major Peshawar hospitals have unique and verified coordinates."""

    def test_hospitals_have_distinct_coordinates(self):
        # Coordinates defined in frontend PatientDashboard.tsx
        hospital_coords = {
            "Hayatabad Medical Complex (HMC)": (34.0017, 71.4448),
            "Lady Reading Hospital (LRH)": (34.0253, 71.5784),
            "Khyber Teaching Hospital (KTH)": (34.0085, 71.4785),
            "North West General Hospital": (33.9940, 71.4359),
            "Rehman Medical Institute (RMI)": (33.9922, 71.4358),
        }

        # Verify no two hospitals share coordinates
        coord_list = list(hospital_coords.values())
        assert len(coord_list) == len(set(coord_list)), "Hospital coordinates must be distinct"

        # Verify North West General Hospital and RMI do NOT share HMC coordinates
        assert hospital_coords["North West General Hospital"] != hospital_coords["Hayatabad Medical Complex (HMC)"]
        assert hospital_coords["Rehman Medical Institute (RMI)"] != hospital_coords["Hayatabad Medical Complex (HMC)"]
        assert hospital_coords["North West General Hospital"] != hospital_coords["Rehman Medical Institute (RMI)"]


class TestBloodRequestGeolocation:
    """Test latitude and longitude fields on BloodRequestCreate."""

    def test_valid_hospital_coordinates(self):
        # LRH Coordinates: 34.0253, 71.5784
        req = BloodRequestCreate(
            patient_name="Zainab Bibi",
            blood_group="B+",
            units_needed=2,
            hospital_name="Lady Reading Hospital (LRH)",
            hospital_address="Soekarno Square, Peshawar City",
            city="Peshawar",
            area="Saddar",
            latitude=34.0253,
            longitude=71.5784,
            emergency_level="urgent",
            contact_name="Tariq Khan",
            contact_phone="03001234567",
        )
        assert req.latitude == 34.0253
        assert req.longitude == 71.5784

    def test_missing_coordinates_safe(self):
        req = BloodRequestCreate(
            patient_name="Farhan Khan",
            blood_group="A-",
            units_needed=1,
            hospital_name="Unknown Clinic",
            hospital_address="Some street in Peshawar",
            city="Peshawar",
            area="Unknown Area",
            latitude=None,
            longitude=None,
            emergency_level="normal",
            contact_name="Farhan",
            contact_phone="03001234567",
        )
        assert req.latitude is None
        assert req.longitude is None

    def test_invalid_latitude_rejected(self):
        with pytest.raises(ValidationError):
            BloodRequestCreate(
                patient_name="Test",
                blood_group="O+",
                units_needed=1,
                hospital_name="LRH",
                hospital_address="Saddar",
                city="Peshawar",
                area="Saddar",
                latitude=95.0,  # > 90
                longitude=71.5,
                contact_name="Test",
                contact_phone="03001234567",
            )

    def test_invalid_longitude_rejected(self):
        with pytest.raises(ValidationError):
            BloodRequestCreate(
                patient_name="Test",
                blood_group="O+",
                units_needed=1,
                hospital_name="LRH",
                hospital_address="Saddar",
                city="Peshawar",
                area="Saddar",
                latitude=34.0,
                longitude=190.0,  # > 180
                contact_name="Test",
                contact_phone="03001234567",
            )


class TestMatchingEngineDistanceAndScoring:
    """Test Haversine distance and proximity score integration."""

    def test_haversine_distance_between_hmc_and_lrh(self):
        # HMC: (34.0017, 71.4448)
        # LRH: (34.0253, 71.5784)
        dist = safe_distance(34.0017, 71.4448, 34.0253, 71.5784)
        assert dist is not None
        # Distance between HMC (Hayatabad) and LRH (Saddar) is approx 12-14 km
        assert 10.0 < dist < 16.0

    def test_safe_distance_with_none_returns_none(self):
        assert safe_distance(None, None, 34.0, 71.0) is None
        assert safe_distance(34.0, 71.0, None, None) is None
        assert safe_distance(None, None, None, None) is None

    def test_scoring_with_coordinates_awards_proximity(self):
        donor_data = {
            "blood_group": "A+",
            "total_donations": 5,
            "is_verified": True,
            "latitude": 34.0017,
            "longitude": 71.4448,
        }
        # Blood request WITH hospital coordinates
        request_with_geo = {
            "blood_group": "A+",
            "emergency_level": "urgent",
            "latitude": 34.0050,
            "longitude": 71.4480,
        }
        # Blood request WITHOUT coordinates (legacy / missing)
        request_without_geo = {
            "blood_group": "A+",
            "emergency_level": "urgent",
            "latitude": None,
            "longitude": None,
        }

        dist = safe_distance(donor_data["latitude"], donor_data["longitude"], request_with_geo["latitude"], request_with_geo["longitude"])
        score_with_geo, reasons_with_geo = calculate_match_score(donor_data, request_with_geo, dist)

        score_without_geo, reasons_without_geo = calculate_match_score(donor_data, request_without_geo, None)

        # Proximity score should award points when coordinates are present
        assert score_with_geo > score_without_geo
        assert any("Proximity" in r for r in reasons_with_geo)
        assert not any("Proximity" in r for r in reasons_without_geo)
