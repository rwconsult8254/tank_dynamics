"""
Concurrency tests for the tank dynamics simulator API.

Tests that multiple WebSocket sessions operate independently under concurrent load.
"""

import pytest
from starlette.testclient import TestClient


def test_concurrent_websocket_sessions(client):
    """Open multiple WebSocket connections and verify all receive independent updates."""
    with (
        client.websocket_connect("/ws") as ws1,
        client.websocket_connect("/ws") as ws2,
        client.websocket_connect("/ws") as ws3,
    ):
        # All clients should receive state updates
        for ws in [ws1, ws2, ws3]:
            data = ws.receive_json()
            assert data["type"] == "state"

        # All should continue receiving updates
        for ws in [ws1, ws2, ws3]:
            data = ws.receive_json()
            assert data["type"] == "state"


def test_independent_setpoint_changes(client):
    """Change setpoint on one session, verify others unaffected."""
    with (
        client.websocket_connect("/ws") as ws1,
        client.websocket_connect("/ws") as ws2,
    ):
        # Get initial states
        ws1.receive_json()
        ws2.receive_json()

        # Change setpoint only on ws1
        ws1.send_json({"type": "setpoint", "value": 4.0})

        # Get next states
        state1 = ws1.receive_json()
        state2 = ws2.receive_json()

        # ws1 should have new setpoint, ws2 should have default
        assert state1["data"]["setpoint"] == 4.0
        assert state2["data"]["setpoint"] == 2.5


def test_rapid_commands_single_session(client):
    """Send multiple commands rapidly on one session."""
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()

        # Send 10 setpoint changes
        for i in range(10):
            ws.send_json({"type": "setpoint", "value": 2.0 + i * 0.1})

        # Session should still be alive and receiving updates
        data = ws.receive_json()
        assert data["type"] == "state"


def test_reset_during_active_session(client):
    """Reset one session while another continues normally."""
    with (
        client.websocket_connect("/ws") as ws1,
        client.websocket_connect("/ws") as ws2,
    ):
        ws1.receive_json()
        ws2.receive_json()

        # Change setpoint on ws1
        ws1.send_json({"type": "setpoint", "value": 4.0})
        ws1.receive_json()

        # Reset ws1
        ws1.send_json({"type": "reset"})

        # Both should still receive updates
        data1 = ws1.receive_json()
        data2 = ws2.receive_json()
        assert data1["type"] == "state"
        assert data2["type"] == "state"


def test_disconnect_one_session(client):
    """Disconnect one session and verify others continue."""
    with (
        client.websocket_connect("/ws") as ws1,
        client.websocket_connect("/ws") as ws2,
    ):
        ws1.receive_json()
        ws2.receive_json()

        # Close ws1
        ws1.close()

        # ws2 should continue receiving
        data = ws2.receive_json()
        assert data["type"] == "state"


def test_history_per_session(client):
    """Each session should have its own history buffer."""
    with (
        client.websocket_connect("/ws") as ws1,
        client.websocket_connect("/ws") as ws2,
    ):
        # Let both sessions accumulate some history
        for _ in range(3):
            ws1.receive_json()
            ws2.receive_json()

        # Request history from both
        ws1.send_json({"type": "history", "duration": 60})
        ws2.send_json({"type": "history", "duration": 60})

        # Both should respond with their own history
        for ws in [ws1, ws2]:
            for _ in range(5):
                data = ws.receive_json()
                if data["type"] == "history":
                    assert isinstance(data["data"], list)
                    break
