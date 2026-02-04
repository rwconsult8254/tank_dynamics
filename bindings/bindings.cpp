/**
 * @file bindings.cpp
 * @brief Python bindings for the Tank Dynamics Simulator using pybind11
 *
 * This file creates the pybind11 module that exposes the C++ simulation
 * library to Python. The module provides a high-performance tank level
 * control simulator with PID feedback control.
 *
 * The module is named _tank_sim (with underscore) to indicate it's the
 * internal C++ extension module. The public Python API is provided by
 * the tank_sim package which imports from this module.
 */

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>

// C++ library headers will be included when full bindings are added
// #include "simulator.h"
// #include "tank_model.h"
// #include "pid_controller.h"
// #include "stepper.h"

namespace py = pybind11;

/**
 * @brief Returns the version string for the tank_sim module.
 * @return Version string in semantic versioning format.
 */
std::string get_version() {
    return "0.1.0";
}

/**
 * @brief pybind11 module definition
 *
 * PYBIND11_MODULE macro creates the Python extension module.
 * The first argument (_tank_sim) becomes the module name.
 * The second argument (m) is the module object used to add bindings.
 */
PYBIND11_MODULE(_tank_sim, m) {
    m.doc() = R"pbdoc(
        Tank Dynamics Simulator - C++ Extension Module
        ===============================================

        This is the internal C++ extension module for the tank_sim package.
        It provides Python bindings to a high-performance simulation engine
        for tank level control with PID feedback.

        Features:
        - Real-time tank material balance (ODE integration using GSL RK4)
        - PID feedback control with anti-windup protection
        - Valve dynamics and flow calculations
        - Step-by-step simulation with configurable time steps

        This module is not intended for direct import. Use the tank_sim
        package instead:

            import tank_sim
            print(tank_sim.get_version())

        Full class bindings (Simulator, SimulatorConfig, etc.) will be
        added in subsequent development tasks.
    )pbdoc";

    // Module version function
    m.def("get_version", &get_version, R"pbdoc(
        Get the version of the tank_sim module.

        Returns:
            str: Version string in semantic versioning format (e.g., "0.1.0").
    )pbdoc");

    // Full class bindings will be added in Task 11:
    // - TankModelParameters
    // - PIDGains
    // - ControllerConfig
    // - SimulatorConfig
    // - Simulator
}
