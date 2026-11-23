"""
Unit and integration tests for BloodBridge FastAPI endpoints.
Tests public metadata, health probe, and basic endpoints using FastAPI TestClient.
"""

from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_health_probe():
    """Verify health check endpoint returns 200 and Peshawar context."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Peshawar" in data["city"]


def test_root_endpoint():
    """Verify root endpoint gives startup details."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "BloodBridge"
    assert "Peshawar" in data["region"]


def test_public_blood_groups():
    """Verify clinical compatibility endpoint."""
    response = client.get("/api/public/blood-groups")
    assert response.status_code == 200
    data = response.json()
    assert "compatibility" in data
    assert data["universal_donor"] == "O-"
    assert data["universal_recipient"] == "AB+"


def test_public_areas():
    """Verify Peshawar areas endpoint includes Hayatabad and Saddar."""
    response = client.get("/api/public/areas")
    assert response.status_code == 200
    areas = response.json()
    assert len(areas) >= 5
    area_names = [a["name"] for a in areas]
    assert "Hayatabad" in area_names
    assert "University Town" in area_names
    assert "Saddar" in area_names


def test_unauthenticated_protected_route():
    """Verify that accessing protected endpoints without a token returns 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
