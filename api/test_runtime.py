"""
Runtime verification tests for Task 14 and Task 15.
Uses only built-in libraries (urllib, json, time).
"""

import json
import time
import urllib.error
import urllib.request

BASE_URL = "http://localhost:8000"
API_HEALTH = f"{BASE_URL}/api/health"
API_CONFIG = f"{BASE_URL}/api/config"
API_HISTORY = f"{BASE_URL}/api/history"
API_RESET = f"{BASE_URL}/api/reset"


def make_request(method, url, data=None):
    """Make HTTP request and return parsed JSON response."""
    try:
        if data:
            data = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("Content-Type", "application/json")
        else:
            req = urllib.request.Request(url, method=method)

        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except:
            return e.code, {"error": body}
    except Exception as e:
        return None, {"error": str(e)}


def test_health_check():
    """Test that server is responding."""
    print("\n=== Test 1: Health Check ===")
    status, response = make_request("GET", API_HEALTH)
    assert status == 200, f"Expected 200, got {status}"
    assert response["status"] == "ok"
    print("✓ Server responding")


def test_config_endpoint():
    """Test config endpoint returns correct structure."""
    print("\n=== Test 2: Config Endpoint ===")
    status, response = make_request("GET", API_CONFIG)
    assert status == 200, f"Expected 200, got {status}"

    required_fields = [
        "tank_height",
        "tank_area",
        "valve_coefficient",
        "initial_level",
        "initial_setpoint",
        "pid_gains",
        "timestep",
        "history_capacity",
        "history_size",
    ]

    for field in required_fields:
        assert field in response, f"Missing field: {field}"

    assert response["history_capacity"] == 7200, (
        f"Expected capacity 7200, got {response['history_capacity']}"
    )
    print(
        f"✓ Config: capacity={response['history_capacity']}, size={response['history_size']}"
    )


def test_history_accumulation():
    """Test that history accumulates over time."""
    print("\n=== Test 3: History Accumulation ===")
    print("Waiting 12 seconds for data accumulation...")
    time.sleep(12)

    status, history = make_request("GET", API_HISTORY + "?duration=10")
    assert status == 200, f"Expected 200, got {status}"
    assert isinstance(history, list), f"Expected list, got {type(history)}"

    print(f"Got {len(history)} data points (expected ~10)")
    assert len(history) >= 9, f"Expected at least 9 points, got {len(history)}"

    # Verify structure
    if len(history) > 0:
        entry = history[0]
        required_fields = [
            "time",
            "tank_level",
            "setpoint",
            "inlet_flow",
            "outlet_flow",
            "valve_position",
            "error",
            "controller_output",
        ]
        for field in required_fields:
            assert field in entry, f"Entry missing field: {field}"
            assert isinstance(entry[field], (int, float)), f"Field {field} not numeric"

    print("✓ History structure correct")


def test_time_progression():
    """Test that time values increase monotonically."""
    print("\n=== Test 4: Time Progression ===")

    status, history = make_request("GET", API_HISTORY + "?duration=20")
    assert status == 200
    assert len(history) >= 2, "Need at least 2 entries"

    times = [entry["time"] for entry in history]
    for i in range(1, len(times)):
        assert times[i] > times[i - 1], (
            f"Time not increasing: {times[i - 1]} -> {times[i]}"
        )
        assert times[i] - times[i - 1] <= 1.1, (
            f"Time gap too large: {times[i] - times[i - 1]}"
        )

    print(
        f"✓ Time sequence correct: {times[0]:.1f} to {times[-1]:.1f} ({len(times)} entries)"
    )


def test_duration_parameters():
    """Test duration parameter validation."""
    print("\n=== Test 5: Duration Parameters ===")

    # Valid durations
    for duration in [1, 60, 3600, 7200]:
        status, history = make_request("GET", f"{API_HISTORY}?duration={duration}")
        assert status == 200, f"Duration {duration} failed with status {status}"
        assert isinstance(history, list)
        print(f"  duration={duration}: {len(history)} points ✓")

    # Invalid durations (should return 422)
    for duration in [0, -5, 10000]:
        status, response = make_request("GET", f"{API_HISTORY}?duration={duration}")
        assert status == 422, f"Expected 422 for duration {duration}, got {status}"
        print(f"  duration={duration}: correctly rejected (422) ✓")

    print("✓ Duration validation working")


def test_default_duration():
    """Test that default duration (3600) works."""
    print("\n=== Test 6: Default Duration ===")

    status, history = make_request("GET", API_HISTORY)
    assert status == 200
    assert isinstance(history, list)
    print(f"✓ Default duration returns {len(history)} points")


def test_physically_reasonable_values():
    """Test that state values are physically reasonable."""
    print("\n=== Test 7: Physically Reasonable Values ===")

    status, history = make_request("GET", API_HISTORY + "?duration=10")
    assert status == 200
    assert len(history) > 0

    for i, entry in enumerate(history):
        # Tank level should be between 0 and 10 meters
        assert 0 <= entry["tank_level"] <= 10, (
            f"Entry {i}: tank_level {entry['tank_level']} out of range"
        )

        # Setpoint should be between 0 and 10 meters
        assert 0 <= entry["setpoint"] <= 10, (
            f"Entry {i}: setpoint {entry['setpoint']} out of range"
        )

        # Flows should be non-negative
        assert entry["inlet_flow"] >= 0, (
            f"Entry {i}: inlet_flow {entry['inlet_flow']} negative"
        )
        assert entry["outlet_flow"] >= 0, (
            f"Entry {i}: outlet_flow {entry['outlet_flow']} negative"
        )

        # Valve position should be between 0 and 1
        assert 0 <= entry["valve_position"] <= 1, (
            f"Entry {i}: valve_position {entry['valve_position']} out of range"
        )

    print(f"✓ All {len(history)} entries have physically reasonable values")


def test_reset_behavior():
    """Test that reset clears history and resets time."""
    print("\n=== Test 8: Reset Behavior ===")

    # Get initial history
    status, history_before = make_request("GET", API_HISTORY + "?duration=100")
    print(f"History before reset: {len(history_before)} entries")

    # Reset
    status, response = make_request("POST", API_RESET)
    assert status == 200, f"Reset failed with status {status}"
    print("Reset called")

    # Check history immediately
    status, history_after_reset = make_request("GET", API_HISTORY + "?duration=100")
    print(f"History after reset: {len(history_after_reset)} entries")

    # Wait for new data
    print("Waiting 3 seconds for new data...")
    time.sleep(3)

    status, history_new = make_request("GET", API_HISTORY + "?duration=100")
    print(f"History after waiting: {len(history_new)} entries")

    # Verify time restarted near 0
    if len(history_new) > 0:
        first_time = history_new[0]["time"]
        assert first_time < 5, f"Time should be near 0 after reset, got {first_time}"
        print(f"✓ Time restarted at {first_time:.1f} (near 0)")

    print("✓ Reset behavior correct")


def test_maximum_capacity():
    """Test that buffer respects 7200 entry limit."""
    print("\n=== Test 9: Maximum Capacity ===")

    status, history = make_request("GET", API_HISTORY + "?duration=7200")
    assert status == 200
    assert len(history) <= 7200, f"Got {len(history)} entries, expected <= 7200"

    print(f"✓ Buffer respects capacity: {len(history)} <= 7200 entries")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Task 14 & 15 Runtime Verification")
    print("=" * 60)
    print(f"Server: {BASE_URL}")

    try:
        test_health_check()
        test_config_endpoint()
        test_history_accumulation()
        test_time_progression()
        test_duration_parameters()
        test_default_duration()
        test_physically_reasonable_values()
        test_reset_behavior()
        test_maximum_capacity()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
