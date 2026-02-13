"""Tests for Brownian inlet flow mode functionality."""

from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from api.simulation import SessionSimulation


@pytest.fixture
def mock_config():
    """Create a mock tank_sim configuration."""
    config = MagicMock()
    config.model_params = MagicMock()
    config.model_params.k_v = 1.0
    config.model_params.max_height = 5.0
    config.model_params.area = 2.0
    config.initial_state = [2.0]
    config.controllers = [MagicMock()]
    config.controllers[0].initial_setpoint = 3.0
    config.controllers[0].gains = MagicMock()
    config.controllers[0].gains.Kc = 1.0
    config.controllers[0].gains.tau_I = 0.5
    config.controllers[0].gains.tau_D = 0.1
    config.dt = 1.0
    return config


@pytest.fixture
def session(mock_config):
    """Create a SessionSimulation instance with mocked simulator."""
    mock_ws = AsyncMock()
    sess = SessionSimulation("test-session", mock_config, mock_ws)

    # Replace with a controllable mock simulator
    sess.simulator = MagicMock()
    sess.simulator.get_state.return_value = [2.0]
    sess.simulator.get_setpoint.return_value = 3.0

    # Track inlet flow for testing
    sess._current_inlet_flow = 1.0

    def mock_get_inputs():
        return [sess._current_inlet_flow, 0.5]

    def mock_set_input(index, value):
        if index == 0:
            sess._current_inlet_flow = value

    sess.simulator.get_inputs = mock_get_inputs
    sess.simulator.set_input = mock_set_input
    sess.simulator.get_error.return_value = 1.0
    sess.simulator.get_controller_output.return_value = 0.5
    sess.simulator.get_time.return_value = 0.0
    sess.simulator.step = MagicMock()
    return sess


def test_brownian_mode_changes_inlet_flow(session):
    """Verify that inlet flow changes between steps in Brownian mode."""
    session.set_inlet_mode("brownian", min_flow=0.8, max_flow=1.2, variance=0.05)
    assert session.inlet_mode == "brownian"

    inlet_flows = []
    for _ in range(10):
        inlet_flows.append(session._current_inlet_flow)
        session.step()

    assert len(set(inlet_flows)) > 1, "Inlet flow should vary with Brownian motion"

    for flow in inlet_flows:
        assert 0.8 <= flow <= 1.2, f"Flow {flow} outside bounds [0.8, 1.2]"


def test_brownian_mode_respects_bounds(session):
    """Verify inlet flow NEVER exceeds bounds with tight bounds and high variance."""
    session.set_inlet_mode("brownian", min_flow=0.95, max_flow=1.05, variance=0.5)

    inlet_flows = []
    for _ in range(50):
        inlet_flows.append(session._current_inlet_flow)
        session.step()

    for flow in inlet_flows:
        assert 0.95 <= flow <= 1.05, f"Flow {flow} exceeded bounds [0.95, 1.05]"


def test_brownian_mode_mean_reversion(session):
    """Verify the mean inlet flow is approximately centered."""
    session.set_inlet_mode("brownian", min_flow=0.5, max_flow=1.5, variance=0.05)

    inlet_flows = []
    for _ in range(1000):
        inlet_flows.append(session._current_inlet_flow)
        session.step()

    mean_flow = np.mean(inlet_flows)
    assert 0.8 <= mean_flow <= 1.2, f"Mean flow {mean_flow} not approximately 1.0"


def test_brownian_variance_effect(session):
    """Verify that higher variance produces higher standard deviation."""
    # Low variance
    session.set_inlet_mode("brownian", min_flow=0.5, max_flow=1.5, variance=0.01)

    low_var_flows = []
    for _ in range(100):
        low_var_flows.append(session._current_inlet_flow)
        session.step()

    low_var_std = np.std(low_var_flows)

    # Reset for high variance
    session._current_inlet_flow = 1.0
    session.set_inlet_mode("brownian", min_flow=0.5, max_flow=1.5, variance=0.2)

    high_var_flows = []
    for _ in range(100):
        high_var_flows.append(session._current_inlet_flow)
        session.step()

    high_var_std = np.std(high_var_flows)

    assert high_var_std > low_var_std, (
        f"High variance ({high_var_std}) should have higher std than "
        f"low variance ({low_var_std})"
    )


def test_constant_mode_disables_brownian(session):
    """Verify inlet flow stops changing after switching to constant mode."""
    session.set_inlet_mode("brownian", min_flow=0.5, max_flow=1.5, variance=0.1)

    for _ in range(5):
        session.step()

    frozen_flow = session._current_inlet_flow

    session.set_inlet_mode("constant", min_flow=0.5, max_flow=1.5, variance=0.0)

    for _ in range(10):
        session.step()
        current_flow = session._current_inlet_flow
        assert current_flow == frozen_flow, (
            f"Inlet flow changed in constant mode: {frozen_flow} -> {current_flow}"
        )


def test_brownian_mode_parameter_validation(session):
    """Verify that valid Brownian parameters are stored correctly."""
    session.set_inlet_mode("brownian", min_flow=0.5, max_flow=1.5, variance=0.05)
    assert session.inlet_mode == "brownian"
    assert session.inlet_mode_params["min"] == 0.5
    assert session.inlet_mode_params["max"] == 1.5
    assert session.inlet_mode_params["variance"] == 0.05


def test_apply_brownian_inlet_direct(session):
    """Test the apply_brownian_inlet method directly."""
    session.set_inlet_mode("brownian", min_flow=0.5, max_flow=1.5, variance=0.1)

    current_flow = 1.0
    new_flows = []

    for _ in range(50):
        new_flow = session.apply_brownian_inlet(current_flow)
        new_flows.append(new_flow)
        current_flow = new_flow

    for flow in new_flows:
        assert 0.5 <= flow <= 1.5, f"Flow {flow} outside bounds"

    assert len(set(new_flows)) > 1, "Flows should vary"


def test_brownian_reset_behavior(session):
    """Verify that reset() resets inlet_mode to constant."""
    session.set_inlet_mode("brownian", min_flow=0.8, max_flow=1.2, variance=0.05)
    assert session.inlet_mode == "brownian"

    session.reset()

    assert session.inlet_mode == "constant"
    assert session.inlet_mode_params["min"] == 0.8
    assert session.inlet_mode_params["max"] == 1.2
    assert session.inlet_mode_params["variance"] == 0.05
