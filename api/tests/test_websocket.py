"""
WebSocket protocol tests for the tank dynamics simulator.

Each WebSocket connection gets its own independent simulation session.
Tests verify connection lifecycle, command handling, session isolation,
and the new reset/history commands.
"""

import pytest
from starlette.testclient import TestClient


def test_websocket_connection(client):
    """Verify that a client can connect to /ws endpoint successfully."""
    with client.websocket_connect("/ws") as ws:
        assert ws is not None


def test_websocket_receives_state_updates(client):
    """Connect to WebSocket and verify state update messages arrive periodically."""
    with client.websocket_connect("/ws") as ws:
        data1 = ws.receive_json()
        assert data1["type"] == "state"
        assert "data" in data1
        assert "tank_level" in data1["data"]
        assert "setpoint" in data1["data"]
        assert "inlet_flow" in data1["data"]

        data2 = ws.receive_json()
        assert data2["type"] == "state"
        assert "data" in data2


def test_websocket_setpoint_command(client):
    """Send a setpoint command and verify acceptance."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()  # initial state

        ws.send_json({"type": "setpoint", "value": 3.0})

        data = ws.receive_json()
        assert data["type"] in ["state", "error"]
        if data["type"] == "error":
            pytest.fail("Setpoint command was rejected")


def test_websocket_pid_command(client):
    """Send a PID gains command and verify acceptance."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()

        ws.send_json({"type": "pid", "Kc": 2.0, "tau_I": 120.0, "tau_D": 15.0})

        data = ws.receive_json()
        assert data["type"] in ["state", "error"]
        if data["type"] == "error":
            pytest.fail("PID command was rejected")


def test_websocket_inlet_flow_command(client):
    """Send an inlet flow command and verify acceptance."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()

        ws.send_json({"type": "inlet_flow", "value": 0.9})

        data = ws.receive_json()
        assert data["type"] in ["state", "error"]
        if data["type"] == "error":
            pytest.fail("Inlet flow command was rejected")


def test_websocket_inlet_mode_command(client):
    """Send an inlet mode command and verify acceptance."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()

        ws.send_json(
            {
                "type": "inlet_mode",
                "mode": "brownian",
                "min": 0.8,
                "max": 1.2,
                "variance": 0.05,
            }
        )

        data = ws.receive_json()
        assert data["type"] in ["state", "error"]
        if data["type"] == "error":
            pytest.fail("Inlet mode command was rejected")


def test_websocket_reset_command(client):
    """Send a reset command and verify the simulation resets."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()  # initial state

        # Change setpoint first
        ws.send_json({"type": "setpoint", "value": 4.0})

        # Reset
        ws.send_json({"type": "reset"})

        # Next state update should reflect reset
        data = ws.receive_json()
        assert data["type"] == "state"


def test_websocket_history_command(client):
    """Send a history request and verify response."""
    with client.websocket_connect("/ws") as ws:
        # Wait for a couple of state updates to build history
        ws.receive_json()
        ws.receive_json()

        # Request history
        ws.send_json({"type": "history", "duration": 60})

        # Look for history response (may receive state updates first)
        for _ in range(5):
            data = ws.receive_json()
            if data["type"] == "history":
                assert "data" in data
                assert isinstance(data["data"], list)
                return

        pytest.fail("Did not receive history response")


def test_websocket_invalid_json(client):
    """Send malformed JSON and verify error handling."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()

        ws.send_text("{invalid json")

        data = ws.receive_json()
        assert data["type"] == "error"
        assert "message" in data


def test_websocket_missing_fields(client):
    """Send a command with missing required fields and verify error."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()

        ws.send_json({"type": "setpoint"})

        data = ws.receive_json()
        assert data["type"] == "error"
        assert "message" in data


def test_websocket_invalid_command_type(client):
    """Send a message with unknown type and verify error response."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()

        ws.send_json({"type": "unknown_command", "value": 123})

        data = ws.receive_json()
        assert data["type"] == "error"
        assert "Unknown" in data.get("message", "")


def test_websocket_session_isolation(client):
    """Two WebSocket connections should have independent simulation state."""
    with (
        client.websocket_connect("/ws") as ws1,
        client.websocket_connect("/ws") as ws2,
    ):
        # Both should receive initial state updates
        data1 = ws1.receive_json()
        data2 = ws2.receive_json()
        assert data1["type"] == "state"
        assert data2["type"] == "state"

        # Change setpoint on ws1 only
        ws1.send_json({"type": "setpoint", "value": 4.5})

        # Get next state from both
        state1 = ws1.receive_json()
        state2 = ws2.receive_json()
        assert state1["type"] == "state"
        assert state2["type"] == "state"

        # ws1 should have setpoint 4.5, ws2 should still have default 2.5
        assert state1["data"]["setpoint"] == 4.5
        assert state2["data"]["setpoint"] == 2.5


def test_websocket_health_shows_active_sessions(client):
    """Verify health endpoint counts active WebSocket sessions."""
    # Before connection
    response = client.get("/api/health")
    initial_count = response.json()["active_sessions"]

    with client.websocket_connect("/ws") as ws1:
        ws1.receive_json()  # wait for session to be created
        response = client.get("/api/health")
        assert response.json()["active_sessions"] == initial_count + 1

        with client.websocket_connect("/ws") as ws2:
            ws2.receive_json()
            response = client.get("/api/health")
            assert response.json()["active_sessions"] == initial_count + 2

    # After disconnect
    response = client.get("/api/health")
    assert response.json()["active_sessions"] == initial_count
