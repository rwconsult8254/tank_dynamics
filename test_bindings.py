#!/usr/bin/env python3
"""
Verification script for Task 11: Simulator class Python bindings

This script tests all the functionality bound in Task 11.
Run with: python test_bindings.py
"""

import numpy as np

import tank_sim


def test_configuration_creation():
    """Test creating and configuring all structures."""
    print("Test 1: Configuration creation")

    # Create structures manually
    params = tank_sim.TankModelParameters()
    params.area = 120.0
    params.k_v = 1.2649
    params.max_height = 5.0

    gains = tank_sim.PIDGains()
    gains.Kc = -1.0
    gains.tau_I = 10.0
    gains.tau_D = 1.0

    controller = tank_sim.ControllerConfig()
    controller.gains = gains
    controller.bias = 0.5
    controller.min_output = 0.0
    controller.max_output = 1.0
    controller.max_integral = 10.0
    controller.measured_index = 0
    controller.output_index = 1
    controller.initial_setpoint = 2.5

    config = tank_sim.SimulatorConfig()
    config.model_params = params
    config.controllers = [controller]
    config.initial_state = np.array([2.5])
    config.initial_inputs = np.array([1.0, 0.5])
    config.dt = 1.0

    print(f"  ✓ Configuration created successfully")
    print(f"    Area: {config.model_params.area} m²")
    print(f"    Initial state: {config.initial_state}")
    print(f"    Controllers: {len(config.controllers)}")
    return config


def test_simulator_construction(config):
    """Test creating a Simulator instance."""
    print("\nTest 2: Simulator construction")

    sim = tank_sim.Simulator(config)

    assert sim.get_time() == 0.0, "Initial time should be 0"
    assert np.allclose(sim.get_state(), [2.5]), "Initial state incorrect"
    assert sim.get_setpoint(0) == 2.5, "Initial setpoint incorrect"

    print(f"  ✓ Simulator created")
    print(f"    Time: {sim.get_time()}s")
    print(f"    State: {sim.get_state()}")
    print(f"    Setpoint: {sim.get_setpoint(0)}")
    return sim


def test_steady_state_stability(sim):
    """Test that steady state remains stable."""
    print("\nTest 3: Steady state stability")

    initial_level = sim.get_state()[0]

    for i in range(100):
        sim.step()
        level = sim.get_state()[0]
        assert abs(level - initial_level) < 0.01, (
            f"Level drifted to {level} after {i + 1} steps"
        )

    assert abs(sim.get_time() - 100.0) < 1e-6, "Time tracking incorrect"

    print(f"  ✓ Steady state stable over 100 steps")
    print(f"    Final time: {sim.get_time()}s")
    print(f"    Final level: {sim.get_state()[0]:.3f}m")


def test_step_response():
    """Test setpoint change response."""
    print("\nTest 4: Step response (setpoint change)")

    config = tank_sim.create_default_config()
    sim = tank_sim.Simulator(config)

    # Change setpoint from 2.5 to 3.0
    sim.set_setpoint(0, 3.0)

    for i in range(200):
        sim.step()

    final_level = sim.get_state()[0]
    assert abs(final_level - 3.0) < 0.1, f"Level didn't reach setpoint: {final_level}"

    print(f"  ✓ Setpoint change response successful")
    print(f"    Target: 3.0m, Final: {final_level:.3f}m")
    print(f"    Error: {sim.get_error(0):.3f}m")


def test_reset_functionality():
    """Test reset() method."""
    print("\nTest 5: Reset functionality")

    config = tank_sim.create_default_config()
    sim = tank_sim.Simulator(config)

    # Run simulation and change things
    sim.set_setpoint(0, 3.5)
    for i in range(50):
        sim.step()

    # Reset
    sim.reset()

    assert sim.get_time() == 0.0, "Time not reset"
    assert np.allclose(sim.get_state(), [2.5]), "State not reset"
    assert sim.get_setpoint(0) == 2.5, "Setpoint not reset"

    print(f"  ✓ Reset successful")
    print(f"    Time: {sim.get_time()}s")
    print(f"    State: {sim.get_state()}")


def test_numpy_array_types():
    """Test numpy array conversions."""
    print("\nTest 6: Numpy array type conversion")

    config = tank_sim.create_default_config()
    sim = tank_sim.Simulator(config)

    state = sim.get_state()
    inputs = sim.get_inputs()

    assert isinstance(state, np.ndarray), "State not numpy array"
    assert isinstance(inputs, np.ndarray), "Inputs not numpy array"
    assert state.dtype == np.float64, "State not float64"
    assert inputs.dtype == np.float64, "Inputs not float64"

    print(f"  ✓ Array types correct")
    print(f"    State type: {type(state)}, dtype: {state.dtype}")
    print(f"    Inputs type: {type(inputs)}, dtype: {inputs.dtype}")


def test_exception_handling():
    """Test invalid operations raise proper exceptions."""
    print("\nTest 7: Exception handling")

    config = tank_sim.create_default_config()
    config.initial_state = np.array([])  # Empty state

    try:
        sim = tank_sim.Simulator(config)
        print("  ✗ Should have raised exception for empty state")
        assert False
    except ValueError as e:
        print(f"  ✓ ValueError raised for invalid config: {e}")

    # Test invalid index
    config = tank_sim.create_default_config()
    sim = tank_sim.Simulator(config)

    try:
        sim.get_setpoint(999)
        print("  ✗ Should have raised exception for invalid index")
        assert False
    except IndexError as e:
        print(f"  ✓ IndexError raised for invalid index: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Task 11 Verification: Simulator Class Python Bindings")
    print("=" * 60)

    print(f"\nModule version: {tank_sim.get_version()}")
    print(f"Available classes: {tank_sim.__all__}\n")

    # Run all tests
    config = test_configuration_creation()
    sim = test_simulator_construction(config)
    test_steady_state_stability(sim)
    test_step_response()
    test_reset_functionality()
    test_numpy_array_types()
    test_exception_handling()

    print("\n" + "=" * 60)
    print("✓ All tests passed! Task 11 complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
