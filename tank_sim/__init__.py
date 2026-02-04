"""
Tank Dynamics Simulator
=======================

A real-time tank level control simulator with PID control.

This package provides Python bindings to a high-performance C++ simulation
engine that models:

- Tank material balance (ODE integration using GSL RK4)
- PID feedback control with anti-windup
- Valve dynamics and flow calculations

Basic usage::

    import tank_sim

    # Check version
    print(tank_sim.get_version())

    # Full API (available after Task 11):
    # config = tank_sim.create_default_config()
    # sim = tank_sim.Simulator(config)
    # sim.step()
    # print(sim.get_state())

"""

__version__ = "0.1.0"

# Import from the C++ extension module
from ._tank_sim import get_version

# Public API - functions and classes exported by this package
__all__ = [
    "get_version",
]
