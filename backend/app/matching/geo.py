"""
Geographic utility functions.

Provides Haversine distance calculation and radius-based filtering
for matching donors with blood requests based on location.
"""

import math
from typing import Optional


# Earth's mean radius in kilometers
EARTH_RADIUS_KM = 6371.0


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points on Earth.

    Uses the Haversine formula to compute the shortest distance over
    the earth's surface between two points specified by latitude and longitude.

    Args:
        lat1: Latitude of point 1 in decimal degrees.
        lon1: Longitude of point 1 in decimal degrees.
        lat2: Latitude of point 2 in decimal degrees.
        lon2: Longitude of point 2 in decimal degrees.

    Returns:
        Distance in kilometers between the two points.
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def is_within_radius(
    lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float
) -> bool:
    """
    Check if two points are within a specified radius of each other.

    Args:
        lat1: Latitude of point 1.
        lon1: Longitude of point 1.
        lat2: Latitude of point 2.
        lon2: Longitude of point 2.
        radius_km: Maximum distance in kilometers.

    Returns:
        True if the distance between points is within the radius.
    """
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_km


def calculate_distance_score(distance_km: float, max_distance_km: float = 50.0) -> float:
    """
    Calculate a score based on distance (closer = higher score).

    Uses an inverse linear scale where 0 km distance yields the maximum
    score and distances beyond max_distance_km yield 0.

    Args:
        distance_km: The actual distance in kilometers.
        max_distance_km: The maximum distance for scoring (beyond this = 0 points).

    Returns:
        A score between 0.0 and 20.0, where closer distances score higher.
    """
    max_score = 20.0
    if distance_km >= max_distance_km:
        return 0.0
    return max_score * (1.0 - (distance_km / max_distance_km))


def safe_distance(
    lat1: Optional[float],
    lon1: Optional[float],
    lat2: Optional[float],
    lon2: Optional[float],
) -> Optional[float]:
    """
    Safely calculate distance, returning None if any coordinate is missing.

    Args:
        lat1: Latitude of point 1 (may be None).
        lon1: Longitude of point 1 (may be None).
        lat2: Latitude of point 2 (may be None).
        lon2: Longitude of point 2 (may be None).

    Returns:
        Distance in km if all coordinates are available, None otherwise.
    """
    if any(coord is None for coord in [lat1, lon1, lat2, lon2]):
        return None
    return haversine_distance(lat1, lon1, lat2, lon2)  # type: ignore[arg-type]
