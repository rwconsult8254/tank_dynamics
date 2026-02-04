# CMakeLists.txt for bindings/ directory
# This directory contains language bindings and verification utilities for the C++ library

# ============================================================================
# VERIFICATION PROGRAMS
# ============================================================================

# Stepper verification program
# Tests RK4 implementation with exponential decay ODE
# Verifies: numerical accuracy and 4th-order convergence
add_executable(stepper_verify stepper_verify.cpp)
target_link_libraries(stepper_verify PRIVATE ${CORE_LIB})

# Simulator verification program
# Tests Simulator instantiation and basic operation
# Verifies: construction, step() execution, and state retrieval
add_executable(simulator_verify simulator_verify.cpp)
target_link_libraries(simulator_verify PRIVATE ${CORE_LIB})

# ============================================================================
# PYTHON BINDINGS
# ============================================================================

# pybind11 Python module
# Creates a Python extension module named _tank_sim that wraps the C++ library
#
# The module is named _tank_sim (with underscore) by convention:
# - The underscore indicates it's the internal C++ extension
# - The public API is provided by tank_sim/__init__.py which imports from _tank_sim
#
# pybind11_add_module() creates a shared library with proper Python extension suffix
# (.cpython-310-x86_64-linux-gnu.so on Linux, .pyd on Windows)

pybind11_add_module(_tank_sim bindings.cpp)

# Link against the core C++ library
# This gives access to all C++ classes (TankModel, PIDController, Stepper, Simulator)
target_link_libraries(_tank_sim PRIVATE ${CORE_LIB})

# Set include directories for pybind11 module
# The core library's public include directories are inherited through the link
target_include_directories(_tank_sim PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../src
)

# Install the Python module
# scikit-build-core handles the installation path automatically
# For manual CMake builds, install to a location Python can find
install(TARGETS _tank_sim
    LIBRARY DESTINATION tank_sim
    RUNTIME DESTINATION tank_sim
)
