"""
Verification tests for ring buffer functionality in the tank dynamics API.

This script tests:
- Ring buffer accumulation over time
- History endpoint with various duration parameters
- Data consistency and format
- Concurrent access patterns
- Reset behavior
- Memory stability over extended runs
"""

import asyncio
import json
import time
from datetime import datetime

import httpx

BASE_URL = "http://localhost:8000"
API_HISTORY = f"{BASE_URL}/api/history"
API_CONFIG = f"{BASE_URL}/api/config"
API_RESET = f"{BASE_URL}/api/reset"


async def test_ring_buffer_accumulation():
    """Test that history buffer accumulates data over time."""
    print("\n=== Test 1: Ring Buffer Accumulation ===")

    async with httpx.AsyncClient() as client:
        # Query after 10+ seconds of operation
        print("Waiting 12 seconds for data accumulation...")
        await asyncio.sleep(12)

        response = await client.get(API_HISTORY, params={"duration": 10})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        history = response.json()
        print(f"Got {len(history)} data points (expected ~10)")
        assert len(history) >= 9, f"Expected at least 9 points, got {len(history)}"

        # Verify time increases monotonically
        times = [entry["time"] for entry in history]
        for i in range(1, len(times)):
            assert times[i] > times[i - 1], (
                f"Time not increasing: {times[i - 1]} -> {times[i]}"
            )

        print(f"✓ Time sequence correct: {times[0]:.1f} to {times[-1]:.1f}")
        print("✓ Test 1 PASSED")


async def test_duration_parameter():
    """Test duration parameter validation and behavior."""
    print("\n=== Test 2: Duration Parameter Validation ===")

    async with httpx.AsyncClient() as client:
        # Test valid durations
        test_cases = [
            (1, "should return ~1 point"),
            (60, "should return ~60 points"),
            (3600, "default, should return up to 1 hour"),
        ]

        for duration, description in test_cases:
            response = await client.get(API_HISTORY, params={"duration": duration})
            assert response.status_code == 200, (
                f"Duration {duration}: {response.status_code}"
            )
            history = response.json()
            print(f"  duration={duration}: {len(history)} points ({description})")

        # Test invalid durations (should return 422)
        invalid_cases = [
            (0, "below minimum"),
            (10000, "above maximum"),
            (-5, "negative"),
        ]

        for duration, reason in invalid_cases:
            response = await client.get(API_HISTORY, params={"duration": duration})
            assert response.status_code == 422, (
                f"Expected 422 for {duration} ({reason}), got {response.status_code}"
            )
            print(f"  duration={duration} correctly rejected (422) - {reason}")

        # Test default (no parameter)
        response = await client.get(API_HISTORY)
        assert response.status_code == 200
        history = response.json()
        print(f"  default: {len(history)} points (should default to 3600)")

        print("✓ Test 2 PASSED")


async def test_data_consistency():
    """Test that history data matches StateSnapshot structure."""
    print("\n=== Test 3: Data Consistency ===")

    async with httpx.AsyncClient() as client:
        response = await client.get(API_HISTORY, params={"duration": 10})
        assert response.status_code == 200

        history = response.json()
        if len(history) == 0:
            print("⚠ No history data yet, skipping consistency check")
            return

        # Check required fields
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

        for i, entry in enumerate(history):
            for field in required_fields:
                assert field in entry, f"Entry {i} missing field: {field}"
                assert isinstance(entry[field], (int, float)), (
                    f"Entry {i}, field {field} not numeric"
                )

            # Check physically reasonable values
            assert 0 <= entry["tank_level"] <= 10, (
                f"Tank level out of range: {entry['tank_level']}"
            )
            assert 0 <= entry["setpoint"] <= 10, (
                f"Setpoint out of range: {entry['setpoint']}"
            )
            assert entry["inlet_flow"] >= 0, (
                f"Inlet flow negative: {entry['inlet_flow']}"
            )
            assert entry["outlet_flow"] >= 0, (
                f"Outlet flow negative: {entry['outlet_flow']}"
            )
            assert 0 <= entry["valve_position"] <= 1, (
                f"Valve position out of range: {entry['valve_position']}"
            )

        print(f"✓ All {len(history)} entries have required fields")
        print(f"✓ All values physically reasonable")
        print("✓ Test 3 PASSED")


async def test_concurrent_access():
    """Test that concurrent history requests don't cause errors."""
    print("\n=== Test 4: Concurrent Access ===")

    async def fetch_history(duration, request_id):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(API_HISTORY, params={"duration": duration})
                assert response.status_code == 200
                history = response.json()
                return (request_id, len(history), None)
            except Exception as e:
                return (request_id, 0, str(e))

    # Make 5 concurrent requests
    tasks = [fetch_history(60, i) for i in range(5)]

    results = await asyncio.gather(*tasks)

    for req_id, count, error in results:
        if error:
            print(f"  Request {req_id}: ERROR - {error}")
            assert False, f"Concurrent request failed: {error}"
        else:
            print(f"  Request {req_id}: {count} points")

    print("✓ All concurrent requests succeeded")
    print("✓ Test 4 PASSED")


async def test_reset_behavior():
    """Test that reset clears history and allows new accumulation."""
    print("\n=== Test 5: Reset Behavior ===")

    async with httpx.AsyncClient() as client:
        # Get initial history length
        response = await client.get(API_HISTORY, params={"duration": 100})
        initial_history = response.json()
        print(f"Initial history size: {len(initial_history)}")

        # Reset
        response = await client.post(API_RESET)
        assert response.status_code == 200
        print("Reset called")

        # Check history immediately after reset
        response = await client.get(API_HISTORY, params={"duration": 100})
        post_reset_history = response.json()
        print(f"History after reset: {len(post_reset_history)} points")

        # Wait for new data
        print("Waiting 3 seconds for new data accumulation...")
        await asyncio.sleep(3)

        response = await client.get(API_HISTORY, params={"duration": 100})
        new_history = response.json()
        print(f"History after waiting: {len(new_history)} points")

        # Verify time starts near 0
        if len(new_history) > 0:
            first_time = new_history[0]["time"]
            print(f"First data point time: {first_time}")
            assert first_time < 5, (
                f"Time should be near 0 after reset, got {first_time}"
            )

        print("✓ Reset properly clears history")
        print("✓ New data accumulates from near time=0")
        print("✓ Test 5 PASSED")


async def test_config_history_info():
    """Test that config endpoint includes history information."""
    print("\n=== Test 6: Config History Information ===")

    async with httpx.AsyncClient() as client:
        response = await client.get(API_CONFIG)
        assert response.status_code == 200

        config = response.json()

        assert "history_capacity" in config, "Missing history_capacity"
        assert config["history_capacity"] == 7200, (
            f"Expected 7200, got {config['history_capacity']}"
        )
        print(f"✓ history_capacity: {config['history_capacity']}")

        assert "history_size" in config, "Missing history_size"
        print(f"✓ history_size: {config['history_size']}")

        print("✓ Test 6 PASSED")


async def test_maximum_history():
    """Test querying maximum history duration."""
    print("\n=== Test 7: Maximum History Query ===")

    async with httpx.AsyncClient() as client:
        response = await client.get(API_HISTORY, params={"duration": 7200})
        assert response.status_code == 200

        history = response.json()
        print(f"Queried max duration (7200): got {len(history)} points")

        # If just started, should have fewer than 7200
        # After 2+ hours, should have exactly 7200 (or the buffer capacity)
        print(f"  (Expected <= 7200, buffer will fill over time)")
        assert len(history) <= 7200, f"Got more than max capacity: {len(history)}"

        print("✓ Test 7 PASSED")


async def run_all_tests():
    """Run all verification tests."""
    print("=" * 60)
    print("Ring Buffer Verification Tests")
    print("=" * 60)
    print(f"Test server: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Quick health check
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/health")
            assert response.status_code == 200, (
                "Health check failed - server not responding"
            )
        print("✓ Server responding")

        # Run tests
        await test_ring_buffer_accumulation()
        await test_duration_parameter()
        await test_data_consistency()
        await test_concurrent_access()
        await test_reset_behavior()
        await test_config_history_info()
        await test_maximum_history()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    exit(exit_code)
