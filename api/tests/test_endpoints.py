"""
REST API endpoint tests for the tank dynamics simulator.

Only health and config endpoints remain as REST — all session-scoped
operations (setpoint, pid, inlet, reset, history) are now WebSocket-only.
"""

import pytest


def test_health_endpoint(client):
    """Verify GET /api/health returns status 200 with active_sessions count."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "active_sessions" in data
    assert data["active_sessions"] >= 0


def test_get_config(client):
    """Verify GET /api/config returns configuration with all required fields."""
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()

    # Check all required fields
    assert "tank_height" in data
    assert "tank_area" in data
    assert "valve_coefficient" in data
    assert "initial_level" in data
    assert "initial_setpoint" in data
    assert "pid_gains" in data
    assert "timestep" in data
    assert "history_capacity" in data
    assert "history_size" in data

    # Verify PID gains structure
    assert "Kc" in data["pid_gains"]
    assert "tau_I" in data["pid_gains"]
    assert "tau_D" in data["pid_gains"]

    # Verify numeric values are reasonable
    assert data["tank_height"] > 0
    assert data["tank_area"] > 0
    assert data["valve_coefficient"] > 0
    assert data["timestep"] > 0
    assert data["history_capacity"] > 0


def test_404_unknown_endpoint(client):
    """Verify requests to non-existent endpoints return 404."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


def test_removed_endpoints_return_404(client):
    """Verify that removed session-scoped REST endpoints return 404/405."""
    # These endpoints were removed — they should not exist
    response = client.get("/api/state")
    assert response.status_code == 404

    response = client.post("/api/setpoint", json={"value": 3.0})
    assert response.status_code == 404

    response = client.post("/api/pid", json={"Kc": 1.5, "tau_I": 100.0, "tau_D": 10.0})
    assert response.status_code == 404

    response = client.post("/api/inlet_flow", json={"value": 1.0})
    assert response.status_code == 404

    response = client.post("/api/inlet_mode", json={"mode": "constant"})
    assert response.status_code == 404

    response = client.post("/api/reset")
    assert response.status_code == 404

    response = client.get("/api/history")
    assert response.status_code == 404
