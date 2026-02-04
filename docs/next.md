# Next Tasks - Tank Dynamics Simulator

## Current Phase: Phase 2 - Python Bindings

**Status:** Starting Phase 2 - C++ simulation core complete and tested

**Progress:** 0% - Phase 2 just beginning

**Phase 1 Completion:**
- ✅ All C++ classes implemented (TankModel, PIDController, Stepper, Simulator)
- ✅ 42 tests passing (100% pass rate)
- ✅ Code review feedback implemented
- ✅ Comprehensive documentation complete
- ✅ Ready for Python bindings

---

## Task 10: Create pybind11 Module Structure

**Phase:** 2 - Python Bindings
**Prerequisites:** Phase 1 complete (all C++ classes implemented and tested)

### Files to Create

- Create `/home/roger/dev/tank_dynamics/bindings/bindings.cpp`
- Create `/home/roger/dev/tank_dynamics/pyproject.toml` (modern Python packaging with scikit-build-core)
- Create `/home/roger/dev/tank_dynamics/tank_sim/__init__.py` (Python package initialization)
- Update `/home/roger/dev/tank_dynamics/bindings/CMakeLists.txt` to build Python module
- Update `/home/roger/dev/tank_dynamics/CMakeLists.txt` to fetch pybind11

### Requirements

This task sets up the infrastructure for exposing the C++ simulation library to Python using pybind11. The goal is to create a Python package called `tank_sim` that can be imported and used from Python code.

#### bindings.cpp specifications:

This file creates the pybind11 module that wraps the C++ classes for Python.

The file should include necessary headers:
- pybind11 headers (pybind11/pybind11.h, pybind11/eigen.h, pybind11/stl.h)
- All C++ class headers (simulator.h, tank_model.h, pid_controller.h, stepper.h)
- Eigen headers for automatic numpy conversion

Define the Python module using the PYBIND11_MODULE macro:
- Module name should be underscore tank_sim (the internal C++ module name)
- Module docstring should describe the package: "Tank Dynamics Simulator - Real-time tank level control simulation with PID control"

For now, just create a minimal working module with a simple test function:
- Add a function called "get_version" that returns a string with the version number "0.1.0"
- Add module docstring explaining this is the Python interface to the C++ simulation core

The full class bindings will be added in subsequent tasks. This task focuses on getting the build infrastructure working.

#### pyproject.toml specifications:

This file configures how the Python package is built and installed using the modern `pyproject.toml` standard with `scikit-build-core`. This approach leverages the existing CMakeLists.txt rather than duplicating build configuration.

**Why scikit-build-core instead of setup.py:**
- `setup.py` is deprecated; `pyproject.toml` is the modern Python packaging standard (PEP 517/518)
- scikit-build-core integrates with CMake, reusing your existing build configuration
- Works seamlessly with `uv` for reproducible virtual environments
- Clean `pip install .` workflow for both development and VPS deployment

The pyproject.toml should contain:

```toml
[build-system]
requires = ["scikit-build-core>=0.8", "pybind11>=2.11"]
build-backend = "scikit_build_core.build"

[project]
name = "tank-sim"
version = "0.1.0"
description = "Real-time tank dynamics simulator with PID control"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Roger"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: C++",
    "Topic :: Scientific/Engineering",
]
dependencies = [
    "numpy>=1.20",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]
api = [
    "fastapi>=0.100",
    "uvicorn[standard]>=0.20",
    "websockets>=11.0",
]

[tool.scikit-build]
cmake.minimum-version = "3.20"
cmake.build-type = "Release"
wheel.packages = ["tank_sim"]

[tool.pytest.ini_options]
testpaths = ["tests/python"]
python_files = ["test_*.py"]
addopts = "-v"
```

**Key configuration notes:**
- `requires-python = ">=3.10"` - Modern Python for better type hints and performance
- `dependencies` includes numpy (required for array conversions)
- `[project.optional-dependencies]` separates dev tools from production dependencies
- `[tool.scikit-build]` tells scikit-build-core to use the existing CMakeLists.txt
- The `wheel.packages` setting ensures the `tank_sim/` Python package is included

#### tank_sim/__init__.py specifications:

This file makes tank_sim a proper Python package and provides the public API.

The file should:
- Import the C++ extension module (from ._tank_sim import *)
- Define package version: `__version__ = "0.1.0"`
- Define what gets exported with `__all__` list (for now just ["get_version"])
- Add module docstring explaining the package purpose

Example structure:
```
Tank Dynamics Simulator
=======================

A real-time tank level control simulator with PID control.

This package provides Python bindings to a high-performance C++ simulation
engine that models:
- Tank material balance (ODE integration using GSL RK4)
- PID feedback control with anti-windup
- Valve dynamics and flow calculations

Basic usage:
    import tank_sim
    # Full API will be available after Task 11
```

#### bindings/CMakeLists.txt update:

Update the existing CMakeLists.txt in bindings/ to build a Python module instead of just verification executables.

The CMakeLists should:
- Find pybind11 using `find_package(pybind11 REQUIRED)`
- Create a Python module target using `pybind11_add_module`
- Module name: tank_sim (without underscore in CMake target)
- Sources: bindings.cpp
- Link against: tank_sim_core library (contains all C++ classes)
- Set output name to _tank_sim (with underscore for Python import)
- Install the module to appropriate location for Python to find it

The module should be installed where Python can import it. scikit-build-core handles this automatically when using `pip install`.

#### CMakeLists.txt updates (root):

Add pybind11 as a FetchContent dependency in the root CMakeLists.txt, similar to how Eigen3 and GoogleTest are handled:

```cmake
# ============================================================================
# PYBIND11 FETCH (for Python bindings)
# ============================================================================
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)
```

This should be added after the GoogleTest fetch and before the library target definition.

Also add Python detection near the top of the file:
```cmake
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
```

### Build and Installation Process

After implementation, the build process uses `uv` for reproducible environments:

**Development workflow (recommended):**
```bash
# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/python/ -v
```

**Production/VPS installation:**
```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install with API dependencies for FastAPI server
uv pip install ".[api]"
```

**CMake-only build (for C++ development/debugging):**
```bash
# Build with CMake as before
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build

# Python module will be in build/bindings/_tank_sim.so
# For quick testing, add to PYTHONPATH:
export PYTHONPATH=$PWD/build/bindings:$PWD:$PYTHONPATH
python -c "import tank_sim; print(tank_sim.get_version())"
```

**Building a wheel for distribution:**
```bash
uv pip install build
python -m build --wheel
# Output: dist/tank_sim-0.1.0-cp310-cp310-linux_x86_64.whl
```

The recommended workflow is using `uv pip install -e ".[dev]"` which handles everything automatically.

### Verification Strategy

After implementing this task, verify the module can be imported:

Create a simple test script `test_import.py`:
```python
import sys
sys.path.insert(0, 'build/bindings')  # Or wherever module was built
import tank_sim

print(f"tank_sim version: {tank_sim.get_version()}")
print("Module imported successfully!")
```

Run the script:
```bash
python test_import.py
```

Expected output:
```
tank_sim version: 0.1.0
Module imported successfully!
```

If this works, the pybind11 infrastructure is correctly set up.

### Edge Cases and Potential Issues

**pybind11 not found:**
- Install via pip: `pip install pybind11`
- Or via package manager: `sudo apt install pybind11-dev` (Ubuntu)
- CMake should find it automatically after installation

**Import errors:**
- Module must be in Python path
- Check that _tank_sim.so (or .pyd) exists in expected location
- Verify all C++ dependencies are linked (GSL, Eigen)

**ABI compatibility:**
- Python module must be compiled with same Python version as runtime
- Use `python3 -m pybind11 --includes` to get correct include paths

**CMake FindPython issues:**
- May need to specify Python version explicitly
- Use `find_package(Python3 REQUIRED COMPONENTS Interpreter Development)`

### Acceptance Criteria

- [ ] bindings/bindings.cpp created with minimal pybind11 module
- [ ] PYBIND11_MODULE macro defines _tank_sim module
- [ ] Module includes get_version() function returning "0.1.0"
- [ ] pyproject.toml created with scikit-build-core configuration
- [ ] tank_sim/__init__.py created with package initialization
- [ ] bindings/CMakeLists.txt updated to build Python module using pybind11
- [ ] Root CMakeLists.txt updated with pybind11 FetchContent
- [ ] Root CMakeLists.txt updated with Python3 find_package
- [ ] Module builds without errors via `uv pip install -e ".[dev]"`
- [ ] Module can be imported from Python: `import tank_sim`
- [ ] get_version() returns "0.1.0" when called from Python
- [ ] No import errors or missing symbols
- [ ] Virtual environment workflow documented and tested

---

## Task 11: Bind Simulator Class to Python

**Phase:** 2 - Python Bindings
**Prerequisites:** Task 10 (pybind11 module structure must exist)

### Files to Modify

- Modify `/home/roger/dev/tank_dynamics/bindings/bindings.cpp`
- Update `/home/roger/dev/tank_dynamics/tank_sim/__init__.py`

### Requirements

This task exposes the Simulator class to Python with all its functionality. This is the main public API that Python users will interact with.

The Simulator class is complex with nested configuration structures, so the bindings must handle:
- Nested structures (Config, ControllerConfig, Parameters, Gains)
- Eigen::VectorXd conversion to/from numpy arrays
- Method overloads and default parameters
- Exception propagation from C++ to Python

#### bindings.cpp modifications:

Add bindings for all the nested structures and the Simulator class.

**Bind TankModel::Parameters structure:**
Create a Python class that mirrors the C++ structure:
- Structure name: "TankModelParameters"
- Fields: area (float), k_v (float), max_height (float)
- All fields should be read-write properties
- Add docstring explaining each field with units

**Bind PIDController::Gains structure:**
Create a Python class for PID gains:
- Structure name: "PIDGains"
- Fields: Kc (float), tau_I (float), tau_D (float)
- All fields should be read-write properties
- Add docstring explaining gain meanings and units

**Bind Simulator::ControllerConfig structure:**
Create a Python class for controller configuration:
- Structure name: "ControllerConfig"
- Fields:
  - gains (PIDGains)
  - bias (float)
  - min_output (float)
  - max_output (float)
  - max_integral (float)
  - measured_index (int)
  - output_index (int)
  - initial_setpoint (float)
- All fields should be read-write properties
- Add comprehensive docstring explaining each field

**Bind Simulator::Config structure:**
Create a Python class for simulator configuration:
- Structure name: "SimulatorConfig"
- Fields:
  - model_params (TankModelParameters)
  - controllers (list of ControllerConfig)
  - initial_state (numpy array, converted from Eigen::VectorXd)
  - initial_inputs (numpy array, converted from Eigen::VectorXd)
  - dt (float)
- Add docstring with example usage

**Bind Simulator class:**
Expose all public methods:
- Constructor: accepts SimulatorConfig
- step() method: advances simulation by one timestep
- getTime() method: returns current time
- getState() method: returns state as numpy array
- getInputs() method: returns inputs as numpy array
- getSetpoint(index) method: returns setpoint for controller
- getControllerOutput(index) method: returns controller output
- getError(index) method: returns control error
- setInput(index, value) method: set an input value
- setSetpoint(index, value) method: change controller setpoint
- setControllerGains(index, gains) method: retune controller
- reset() method: return to initial conditions

Add comprehensive docstrings to the class and each method explaining:
- Purpose and behavior
- Parameters and return types
- Units where applicable
- Usage examples

**Handle Eigen::VectorXd conversion:**
- Use pybind11/eigen.h for automatic numpy array conversion
- Include proper header: `#include <pybind11/eigen.h>`
- Eigen vectors automatically become numpy arrays in Python
- Numpy arrays automatically become Eigen vectors in C++

**Handle std::vector conversion:**
- Use pybind11/stl.h for automatic list conversion
- Include proper header: `#include <pybind11/stl.h>`
- std::vector becomes Python list automatically

**Exception handling:**
- C++ exceptions automatically propagate to Python
- std::invalid_argument becomes ValueError
- std::out_of_range becomes IndexError
- std::runtime_error becomes RuntimeError
- No special handling needed, pybind11 does this automatically

#### tank_sim/__init__.py modifications:

Update the package initialization to export the bound classes:

- Import all classes from _tank_sim module
- Update `__all__` list to include:
  - "Simulator"
  - "SimulatorConfig"
  - "ControllerConfig"
  - "TankModelParameters"
  - "PIDGains"
  - "get_version"

Add a convenience function to create a default configuration:
- Function name: create_default_config()
- Returns SimulatorConfig with standard steady-state values
- Uses constants from plan.md:
  - Tank: area=120.0, k_v=1.2649, max_height=5.0
  - Initial state: [2.5] (50% level)
  - Initial inputs: [1.0, 0.5] (inlet flow, valve position)
  - PID gains: Kc=-1.0, tau_I=10.0, tau_D=1.0 (negative Kc for reverse-acting)
  - dt=1.0 second

This provides an easy way for users to get started without manually configuring everything.

### Python API Example

After implementation, users should be able to write:

```python
import tank_sim
import numpy as np

# Create configuration
config = tank_sim.create_default_config()

# Or manually:
config = tank_sim.SimulatorConfig()
config.model_params = tank_sim.TankModelParameters(
    area=120.0,
    k_v=1.2649,
    max_height=5.0
)
config.controllers = [
    tank_sim.ControllerConfig(
        gains=tank_sim.PIDGains(Kc=-1.0, tau_I=10.0, tau_D=1.0),
        bias=0.5,
        min_output=0.0,
        max_output=1.0,
        max_integral=10.0,
        measured_index=0,
        output_index=1,
        initial_setpoint=2.5
    )
]
config.initial_state = np.array([2.5])
config.initial_inputs = np.array([1.0, 0.5])
config.dt = 1.0

# Create simulator
sim = tank_sim.Simulator(config)

# Run simulation
for i in range(100):
    sim.step()
    state = sim.get_state()
    time = sim.get_time()
    print(f"t={time:.1f}, level={state[0]:.3f}")

# Change setpoint
sim.set_setpoint(0, 3.0)

# Continue simulation
for i in range(100):
    sim.step()
```

### Verification Strategy

Create a Python test script `test_bindings.py`:

Test 1: Configuration creation
- Create SimulatorConfig with all parameters
- Verify all fields are accessible
- Verify types are correct (numpy arrays, not lists)

Test 2: Simulator construction
- Create Simulator with valid config
- Should succeed without exceptions

Test 3: Steady state
- Create Simulator at steady state
- Run 100 steps
- Verify state doesn't change significantly

Test 4: Setpoint change
- Start at steady state
- Change setpoint
- Verify level moves toward new setpoint

Test 5: Exception handling
- Try to create Simulator with invalid config
- Should raise ValueError (from std::invalid_argument)
- Try to access invalid controller index
- Should raise IndexError (from std::out_of_range)

### Edge Cases

**Numpy array type conversion:**
- Numpy arrays might be float32 or float64
- pybind11/eigen.h handles this automatically
- Prefer float64 for numerical accuracy

**Python list vs numpy array:**
- Users might pass Python lists instead of numpy arrays
- pybind11 can convert lists to Eigen vectors automatically
- Document that numpy arrays are preferred

**Object lifetime:**
- Simulator owns all internal data
- Python garbage collection will clean up properly
- No manual memory management needed

**Thread safety:**
- Simulator is not thread-safe (document this)
- Each thread should have its own Simulator instance

### Acceptance Criteria

- [ ] TankModelParameters bound to Python with all fields
- [ ] PIDGains bound to Python with all fields
- [ ] ControllerConfig bound to Python with all fields
- [ ] SimulatorConfig bound to Python with all fields
- [ ] Simulator class bound with all methods
- [ ] All methods have comprehensive docstrings
- [ ] pybind11/eigen.h included for numpy conversion
- [ ] pybind11/stl.h included for vector conversion
- [ ] tank_sim/__init__.py updated to export all classes
- [ ] create_default_config() convenience function added
- [ ] Module builds without errors
- [ ] test_bindings.py script created and runs successfully
- [ ] Configuration can be created from Python
- [ ] Simulator can be instantiated from Python
- [ ] All getter methods return correct types (numpy arrays)
- [ ] All setter methods accept correct types
- [ ] Exceptions propagate correctly to Python
- [ ] Steady state test passes
- [ ] Setpoint change test passes
- [ ] Documentation includes Python usage examples

---

## Task 12: Write Python Tests Using pytest

**Phase:** 2 - Python Bindings
**Prerequisites:** Task 11 (Simulator must be bound to Python)

### Files to Create

- Create `/home/roger/dev/tank_dynamics/tests/python/test_simulator_bindings.py`
- Create `/home/roger/dev/tank_dynamics/tests/python/__init__.py` (empty, makes it a package)
- Create `/home/roger/dev/tank_dynamics/tests/python/conftest.py` (pytest fixtures)

**Note:** pytest configuration is already included in `pyproject.toml` (see Task 10), so no separate `pytest.ini` is needed.

### Requirements

This task creates comprehensive Python tests that verify the bindings work correctly. These tests are similar to the C++ tests but written in Python using pytest.

The tests serve two purposes:
1. Verify the Python bindings expose all C++ functionality correctly
2. Provide usage examples for Python users

#### conftest.py specifications:

This file provides pytest fixtures (reusable test components).

Create fixtures:

**default_config fixture:**
- Returns a standard SimulatorConfig at steady state
- Uses the same parameters as C++ tests
- Can be reused across multiple test functions

**steady_state_simulator fixture:**
- Creates a Simulator instance with default_config
- Returns the initialized simulator
- Fixture scope: function (new instance per test)

Example structure:
```python
import pytest
import tank_sim
import numpy as np

@pytest.fixture
def default_config():
    """Standard steady-state configuration"""
    config = tank_sim.create_default_config()
    return config

@pytest.fixture
def steady_state_simulator(default_config):
    """Simulator initialized at steady state"""
    return tank_sim.Simulator(default_config)
```

#### test_simulator_bindings.py specifications:

Create comprehensive test cases covering all functionality.

**Test: Configuration Creation**
- Test name: test_configuration_creation
- Create TankModelParameters, PIDGains, ControllerConfig, SimulatorConfig
- Verify all fields can be set and retrieved
- Verify types are correct
- Assert that numpy arrays are used (not lists)

**Test: Simulator Construction**
- Test name: test_simulator_construction
- Use steady_state_simulator fixture
- Verify simulator is created without errors
- Verify initial time is 0.0
- Verify initial state matches config.initial_state

**Test: Steady State Stability**
- Test name: test_steady_state_stability
- Use steady_state_simulator fixture
- Run 100 steps
- At each step, verify level remains near 2.5 m (within 0.01 tolerance)
- Verify time advances correctly (should reach 100.0 seconds)
- This mirrors the C++ steady state test

**Test: Step Response Increase**
- Test name: test_step_response_increase
- Start at steady state (level 2.5 m)
- Change setpoint to 3.0 m using set_setpoint method
- Run 200 steps
- Verify level increases toward 3.0 m
- After 200 steps, level should be within 0.1 m of setpoint
- Verify valve closes (controller output decreases) to reduce outlet flow

**Test: Step Response Decrease**
- Test name: test_step_response_decrease
- Start at steady state (level 2.5 m)
- Change setpoint to 2.0 m
- Run 200 steps
- Verify level decreases toward 2.0 m
- After 200 steps, level should be close to setpoint
- Verify valve opens (controller output increases)

**Test: Disturbance Rejection**
- Test name: test_disturbance_rejection
- Start at steady state
- Run 50 steps to establish baseline
- Change inlet flow from 1.0 to 1.2 using set_input method
- Run 200 more steps
- Verify level returns to setpoint despite disturbance
- Controller should compensate by adjusting valve

**Test: Reset Functionality**
- Test name: test_reset
- Create simulator at steady state
- Run 50 steps
- Change setpoint to 3.5 m
- Run 50 more steps (system now in transient)
- Record current state
- Call reset()
- Verify time is 0.0
- Verify state is back to initial values
- Verify setpoint is back to initial value
- Run again and verify behavior is reproducible

**Test: Invalid Configuration**
- Test name: test_invalid_configuration
- Attempt to create simulator with invalid config (empty state vector)
- Use pytest.raises to expect ValueError
- Verify exception message is descriptive

**Test: Invalid Controller Index**
- Test name: test_invalid_controller_index
- Create valid simulator
- Attempt to call get_setpoint with index 999 (out of bounds)
- Use pytest.raises to expect IndexError

**Test: Numpy Array Conversion**
- Test name: test_numpy_array_types
- Create simulator
- Call get_state() and verify return type is numpy.ndarray
- Call get_inputs() and verify return type is numpy.ndarray
- Verify arrays are float64 (double precision)
- Verify arrays have correct shape

**Test: Dynamic Retuning**
- Test name: test_dynamic_retuning
- Create simulator
- Run 50 steps
- Create new PIDGains with different values
- Call set_controller_gains method
- Change setpoint
- Continue running
- Verify system responds with new dynamics

### Test Execution

After implementation, run tests with:

```bash
# Run all Python tests
pytest tests/python/ -v

# Run with coverage
pytest tests/python/ --cov=tank_sim --cov-report=html

# Run specific test
pytest tests/python/test_simulator_bindings.py::test_steady_state_stability -v
```

All tests should pass.

### Test Documentation

Each test should include:
- Docstring explaining what is being tested
- Comments explaining expected behavior
- Clear assertion messages

Example:
```python
def test_steady_state_stability(steady_state_simulator):
    """Verify that steady state remains stable over time.
    
    At steady state, all derivatives should be zero, so the system
    should not drift. This tests both numerical stability and
    correct initialization.
    """
    sim = steady_state_simulator
    
    for i in range(100):
        sim.step()
        state = sim.get_state()
        level = state[0]
        
        # Level should remain at initial setpoint
        assert abs(level - 2.5) < 0.01, \
            f"Level drifted to {level} after {i+1} steps"
    
    # Time should have advanced correctly
    assert abs(sim.get_time() - 100.0) < 1e-6, \
        "Time tracking is incorrect"
```

### Comparison with C++ Tests

These Python tests should verify the same behavior as C++ tests:
- Steady state stability
- Step response
- Disturbance rejection
- Reset functionality
- Exception handling

If Python tests pass but C++ tests fail (or vice versa), there's a problem with the bindings or the underlying implementation.

### Acceptance Criteria

- [ ] tests/python/__init__.py created (empty)
- [ ] tests/python/conftest.py created with fixtures
- [ ] default_config fixture provides standard configuration
- [ ] steady_state_simulator fixture provides initialized simulator
- [ ] test_simulator_bindings.py created with all test cases
- [ ] Configuration creation test implemented
- [ ] Simulator construction test implemented
- [ ] Steady state stability test implemented
- [ ] Step response increase test implemented
- [ ] Step response decrease test implemented
- [ ] Disturbance rejection test implemented
- [ ] Reset functionality test implemented
- [ ] Invalid configuration test implemented
- [ ] Invalid controller index test implemented
- [ ] Numpy array conversion test implemented
- [ ] Dynamic retuning test implemented
- [ ] All tests have clear docstrings and comments
- [ ] Tests use pytest fixtures for setup
- [ ] pytest runs without errors: `pytest tests/python/ -v`
- [ ] All tests pass
- [ ] Coverage report shows good coverage of bindings
- [ ] Tests provide usage examples for Python users

---

## Development Environment Setup

This section covers setting up a reproducible development environment using `uv`, the modern Python package manager. This same workflow applies to both local development and VPS deployment.

### Prerequisites

#### System Dependencies (Ubuntu 22.04/24.04 - typical VPS)

```bash
# Update package lists
sudo apt update

# Install build essentials and CMake
sudo apt install -y build-essential cmake

# Install GSL (GNU Scientific Library) - required for ODE integration
sudo apt install -y libgsl-dev

# Install Python development headers
sudo apt install -y python3-dev python3-pip

# Verify installations
cmake --version    # Should be >= 3.20
gsl-config --version  # Should show GSL version
python3 --version  # Should be >= 3.10
```

#### System Dependencies (Arch Linux)

```bash
# Install build tools and GSL
sudo pacman -S base-devel cmake gsl python

# Verify
cmake --version
python --version
```

### Installing uv

`uv` is a fast Python package manager that provides reproducible environments:

```bash
# Install uv (works on Linux and macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to ~/.bashrc or ~/.zshrc for persistence)
source $HOME/.local/bin/env

# Verify installation
uv --version
```

### Development Workflow

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd tank_dynamics

# Create virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install in development mode with dev dependencies
uv pip install -e ".[dev]"

# Verify the installation
python -c "import tank_sim; print(f'tank_sim {tank_sim.__version__}')"

# Run C++ tests
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure

# Run Python tests
pytest tests/python/ -v
```

### VPS Deployment Workflow

For deploying the FastAPI backend on a VPS:

```bash
# SSH into your VPS
ssh user@your-vps.example.com

# Install system dependencies (see Prerequisites above)

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Clone/update the repository
git clone <repository-url> tank_dynamics
cd tank_dynamics

# Create production virtual environment
uv venv

# Activate
source .venv/bin/activate

# Install with API dependencies (FastAPI, uvicorn, etc.)
uv pip install ".[api]"

# Verify
python -c "import tank_sim; import fastapi; print('Ready!')"

# Run the API server (Phase 3)
# uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Troubleshooting

**CMake can't find GSL:**
```bash
# Verify GSL is installed
pkg-config --modversion gsl

# If not found, install it
sudo apt install libgsl-dev  # Ubuntu
sudo pacman -S gsl           # Arch
```

**Python version mismatch:**
```bash
# Check Python version
python3 --version

# If < 3.10, install a newer version
sudo apt install python3.11 python3.11-dev python3.11-venv

# Create venv with specific Python
uv venv --python python3.11
```

**pybind11 compilation errors:**
```bash
# Ensure Python dev headers match your Python version
sudo apt install python3-dev

# Clear build cache and rebuild
rm -rf build/ .venv/
uv venv
uv pip install -e ".[dev]"
```

**Import errors after installation:**
```bash
# Verify the module was installed
python -c "import tank_sim; print(tank_sim.__file__)"

# Check for missing shared libraries
ldd $(python -c "import tank_sim._tank_sim as m; print(m.__file__)")
```

---

## Upcoming Work (After Task 12)

Once Python bindings are tested, Phase 2 will be complete. The next phase will be:

**Phase 3: FastAPI Backend**

Tasks will include:
13. Create FastAPI application structure
14. Implement WebSocket endpoint for real-time data streaming
15. Implement REST endpoints for control actions
16. Create ring buffer for historical data storage
17. Write API integration tests

The FastAPI backend will use the Python bindings to orchestrate the simulation and provide a web API for the frontend.

---

## Notes

**Phase 2 Philosophy:**

The Python bindings should feel natural to Python users while exposing the full power of the C++ simulation. Key principles:

- Use numpy arrays (not lists) for numerical data
- Follow Python naming conventions (snake_case for functions, PascalCase for classes)
- Provide convenience functions (like create_default_config)
- Comprehensive docstrings in Python style
- Proper exception handling

**Testing Philosophy:**

Python tests serve multiple purposes:
- Verify bindings correctness
- Provide usage documentation
- Catch regression errors
- Validate numpy conversion

**Performance Note:**

The Python bindings have minimal overhead. Most time is spent in C++ code (ODE integration, PID calculations). Python-side object creation and method calls add negligible latency for 1 Hz updates.

**Next Phase Preview:**

The FastAPI backend will look like:

```python
from fastapi import FastAPI, WebSocket
import tank_sim

app = FastAPI()
simulator = tank_sim.Simulator(tank_sim.create_default_config())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        simulator.step()
        state = {
            "time": simulator.get_time(),
            "level": simulator.get_state()[0],
            "setpoint": simulator.get_setpoint(0)
        }
        await websocket.send_json(state)
        await asyncio.sleep(1.0)
```

---

*Generated: 2026-02-04*
*Senior Engineer: Claude (Sonnet)*
