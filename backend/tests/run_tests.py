"""
Standalone test runner for BloodBridge intelligent matching engine.
Executes without external dependencies using Python standard library.
"""

import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.matching.compatibility import (
    COMPATIBILITY_MAP,
    is_compatible,
    get_compatible_donor_groups,
)
from app.matching.geo import haversine_distance, is_within_radius
from app.matching.scoring import calculate_match_score


def run_all_tests():
    print("=" * 60)
    print("  BLOODBRIDGE — INTELLIGENT MATCHING ENGINE TEST SUITE")
    print("=" * 60)
    passed = 0
    failed = 0

    # Test 1: O- Universal Donor
    try:
        for recipient in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            assert is_compatible('O-', recipient) is True
        print("[PASS] Test 1: O- is universal red blood cell donor for all groups")
        passed += 1
    except AssertionError as e:
        print("[FAIL] Test 1: O- universal donor failed", e)
        failed += 1

    # Test 2: AB+ Universal Recipient
    try:
        for donor in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            assert is_compatible(donor, 'AB+') is True
        print("[PASS] Test 2: AB+ can safely receive from all ABO/Rh donor groups")
        passed += 1
    except AssertionError as e:
        print("[FAIL] Test 2: AB+ universal recipient failed", e)
        failed += 1

    # Test 3: Standard Clinical Incompatibilities
    try:
        assert is_compatible('A+', 'O-') is False
        assert is_compatible('B+', 'A+') is False
        assert is_compatible('AB+', 'B+') is False
        assert is_compatible('O+', 'O-') is False
        print("[PASS] Test 3: Incompatible blood groups correctly blocked")
        passed += 1
    except AssertionError as e:
        print("[FAIL] Test 3: Incompatibility check failed", e)
        failed += 1

    # Test 4: Haversine Geo Calculation (Peshawar Coordinates)
    try:
        # Hayatabad (34.0017, 71.4448) to University Town (34.0085, 71.4785)
        dist = haversine_distance(34.0017, 71.4448, 34.0085, 71.4785)
        assert 2.5 <= dist <= 4.0
        print(f"[PASS] Test 4: Hayatabad to University Town distance = {round(dist, 2)} km")
        passed += 1
    except AssertionError as e:
        print("[FAIL] Test 4: Distance calculation failed", e)
        failed += 1

    # Test 5: Same Point Distance
    try:
        dist_zero = haversine_distance(34.0151, 71.5249, 34.0151, 71.5249)
        assert dist_zero == 0.0
        print("[PASS] Test 5: Coincident coordinates yield 0.0 km")
        passed += 1
    except AssertionError as e:
        print("[FAIL] Test 5: Coincident coordinates failed", e)
        failed += 1

    # Test 6: Composite Match Scoring
    try:
        donor = {
            'id': 'donor-pesh-01',
            'blood_group': 'B+',
            'area': 'Hayatabad',
            'is_available': True,
            'is_verified': True,
            'total_donations': 4,
        }
        req = {
            'blood_group': 'B+',
            'area': 'Hayatabad',
            'emergency_level': 'critical',
        }
        score, reasons = calculate_match_score(donor, req, distance_km=1.8)
        assert score > 80.0
        assert any('Exact blood group' in r for r in reasons)
        assert any('Critical emergency' in r for r in reasons)
        print(f"[PASS] Test 6: Composite scoring engine (Score: {score} pts)")
        print(f"       Reasons: {reasons}")
        passed += 1
    except AssertionError as e:
        print("[FAIL] Test 6: Scoring calculation failed", e)
        failed += 1

    # Test 7: Exact vs Compatible Priority
    try:
        exact_d = {'id': 'd_exact', 'blood_group': 'A+', 'area': 'Saddar', 'is_available': True, 'is_verified': False, 'total_donations': 0}
        comp_d = {'id': 'd_comp', 'blood_group': 'O+', 'area': 'Saddar', 'is_available': True, 'is_verified': False, 'total_donations': 0}
        req_a = {'blood_group': 'A+', 'area': 'Saddar', 'emergency_level': 'normal'}

        s_exact, _ = calculate_match_score(exact_d, req_a, distance_km=5.0)
        s_comp, _ = calculate_match_score(comp_d, req_a, distance_km=5.0)
        assert s_exact > s_comp
        print(f"[PASS] Test 7: Exact match ({s_exact} pts) > Compatible ({s_comp} pts)")
        passed += 1
    except AssertionError as e:
        print("[FAIL] Test 7: Exact vs compatible comparison failed", e)
        failed += 1

    print("=" * 60)
    print(f"  RESULTS: {passed} PASSED, {failed} FAILED")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
