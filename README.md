# Tank Dynamics Simulator

A real-time tank level control simulator with a SCADA-style interface. The system models a tank with variable inlet flow and PID-controlled outlet valve, allowing operators to experiment with control parameters and observe process dynamics.

## Overview

Tank Dynamics is a proof-of-concept process simulation and control system. It demonstrates real-time simulation of a liquid tank with tunable PID level control. Process operators can monitor tank level, flow rates, and valve position in real-time, while experimenting with different PID controller tuning parameters to understand process control behavior.

## Features

- **Real-time Simulation**: Physics-based tank model running at 1 Hz with RK4 numerical integration
- **PID Control Loop**: Fully tunable proportional-integral-derivative controller for tank level setpoint
- **SCADA Interface**: Modern web-based operator interface with live process visualization
- **Trend Plotting**: Historical data visualization with configurable time ranges
- **Manual & Auto Inlet Modes**: Manual inlet flow control or simulated Brownian motion disturbances
- **Persistent Data**: Up to 2 hours of process history for analysis

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (Next.js)                        │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐  │
│  │    Process View (Tab)   │  │     Trends View (Tab)       │  │
│  │  - Tank visualization   │  │  - Level vs Setpoint plot   │  │
│  │  - PID controls         │  │  - Flow plots (in/out)      │  │
│  │  - Flow indicators      │  │  - Valve position           │  │
│  │  - Setpoint input       │  │  - Historical data          │  │
│  └─────────────────────────┘  └─────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │ WebSocket (1 Hz updates)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Server (Python)                      │
│  - WebSocket endpoint for real-time state                       │
│  - REST endpoints for control and history                       │
│  - Simulation orchestration (1 Hz tick rate)                    │
│  - Ring buffer history (~2 hours of data)                       │
└────────────────────────────────┬────────────────────────────────┘
                                 │ pybind11
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                 C++ Simulation Library                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Tank Model  │  │ PID Control  │  │  RK4 Stepper (GSL)   │  │
│  │  - ODEs      │  │  - Gains     │  │  - Fixed timestep    │  │
│  │  - Valve     │  │  - Integral  │  │  - State integration │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                           Eigen (vectors/matrices)              │
└─────────────────────────────────────────────────────────────────┘
```

**Components:**
- **C++ Simulation Core** (`libsim`): High-performance physics engine using GSL RK4 integrator and Eigen linear algebra
- **Python Bindings** (`tank_sim`): pybind11 interface exposing simulation to Python
- **FastAPI Backend** (`api/`): Real-time WebSocket server orchestrating simulation
- **Next.js Frontend** (`frontend/`): Modern React-based SCADA interface with Tailwind CSS styling

## Quick Start

### Prerequisites

**System Dependencies:**

Ubuntu/Debian:
```bash
sudo apt-get install cmake libgsl-dev build-essential
```

Arch Linux:
```bash
sudo pacman -S cmake gsl base-devel
```

macOS:
```bash
brew install cmake gsl
```

**Development Tools:**
- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- C++17 capable compiler (GCC 9+, Clang 10+, MSVC 2019+)

### Building the C++ Core

```bash
# Configure build system (downloads Eigen, GSL, GoogleTest automatically)
cmake -B build -S .

# Compile C++ library and tests
cmake --build build

# Run test suite
ctest --test-dir build --output-on-failure
```

### Running the Complete System

```bash
# Start backend (requires C++ library built first)
pip install -e .  # Install Python bindings
python -m api.main

# In another terminal, start frontend
cd frontend
npm install
npm run dev
```

Then open http://localhost:3000 in your browser.

## Project Structure

```
tank_dynamics/
├── CMakeLists.txt              # C++ build configuration
├── src/                        # C++ simulation library
│   ├── tank_model.h            # Tank physics model
│   ├── tank_model.cpp
│   ├── pid_controller.h        # PID controller with state
│   ├── pid_controller.cpp
│   ├── stepper.h               # GSL RK4 integrator wrapper
│   ├── stepper.cpp
│   ├── simulator.h             # Main simulation orchestrator
│   └── simulator.cpp
├── bindings/                   # pybind11 Python bindings
│   └── bindings.cpp
├── tests/                      # C++ unit tests (GoogleTest)
│   ├── test_tank_model.cpp
│   ├── test_pid_controller.cpp
│   ├── test_stepper.cpp
│   └── test_simulator.cpp
├── api/                        # FastAPI backend
│   ├── main.py                 # WebSocket server
│   ├── simulation.py           # Simulation loop
│   └── models.py               # Data models
├── frontend/                   # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── components/
│   │       ├── ProcessView.tsx
│   │       ├── TrendsView.tsx
│   │       └── TankGraphic.tsx
│   ├── tailwind.config.js
│   └── package.json
├── docs/                       # Project documentation
│   ├── specs.md                # Feature specifications
│   ├── plan.md                 # Architecture & design plan
│   └── next.md                 # Upcoming tasks
└── CLAUDE.md                   # AI workflow configuration
```

## Process Dynamics

### Tank Model

The tank is modeled as a first-order system with one state variable (liquid level `h`):

```
Material Balance: dh/dt = (q_in - q_out) / A
Valve Equation:   q_out = k_v * x * sqrt(h)
```

Where:
- `h`: Tank level (meters)
- `q_in`: Inlet volumetric flow (m³/s)
- `q_out`: Outlet volumetric flow (m³/s)
- `A`: Cross-sectional area = 120 m²
- `k_v`: Valve coefficient = 1.2649 m^2.5/s
- `x`: Valve position (0 = closed, 1 = fully open)

### Control Loop

The PID controller continuously compares tank level against the setpoint and outputs a valve position (0-1):

```
error = setpoint - actual_level
valve_position = Kc * (error + (1/tau_I) * ∫error + tau_D * d(error)/dt)
```

The controller gains are tunable in real-time:
- **Kc** (proportional gain): Larger = more aggressive response
- **tau_I** (integral time): Smaller = faster offset correction
- **tau_D** (derivative time): Larger = more damping of oscillations

## Development Guide

### Documentation

**For Developers:**
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Setup, building, testing, and development workflow
- **[API Reference](docs/API_REFERENCE.md)** - Complete C++ class documentation with examples
- **[Architecture Plan](docs/plan.md)** - System design, technology decisions, and phase breakdown

**For Understanding the Project:**
- **[Process Specifications](docs/specs.md)** - Feature requirements and acceptance criteria
- **[Tank Dynamics Theory](docs/TankDynamics.md)** - Process physics and control theory
- **[Detailed Class Specifications](docs/)** - `Model Class.md`, `PID Controller Class.md`, `Stepper Class.md`, `Simulator Class.md`

**For Current Work:**
- **[Project Status](docs/STATUS.md)** - Detailed progress report and completed work
- **[Next Tasks](docs/next.md)** - Current implementation phase and upcoming work

### Workflow Roles

This project uses a structured AI-assisted workflow:

| Role | Model | Responsibility |
|------|-------|-----------------|
| Architect | Claude Opus | Strategic planning & design |
| Senior Engineer | Claude Sonnet | Task breakdown & prioritization |
| Engineer | Local LLM + Human | Implementation |
| Code Reviewer | Claude Sonnet | Quality assurance |
| Documentation | Claude Haiku | User/developer documentation |

See `CLAUDE.md` for detailed role definitions and boundaries.

### Current Phase: Phase 1 - C++ Simulation Core

**Progress:** 50% complete - Core simulation library implemented and tested
- ✅ Task 1: Initialize CMake build system
- ✅ Task 2: Implement TankModel class (7 passing tests)
- ✅ Task 3: Write TankModel unit tests
- ✅ Task 4: Implement PIDController class (10 passing tests)
- ✅ Task 5: Write PIDController unit tests
- 🔄 Task 6: Implement Stepper (GSL integration) - In Progress
- ⏳ Task 7: Implement Simulator orchestrator
- ⏳ Task 8: Write comprehensive Simulator tests

### Running Tests

```bash
# C++ tests
ctest --test-dir build --output-on-failure

# C++ tests with detailed output
./build/tests/test_tank_model --gtest_detail=all

# Python tests (after bindings built)
pytest api/tests/ -v
```

### IDE Setup (clangd)

For proper code completion and go-to-definition:

```bash
# From project root - create symlink to compile database
ln -sf build/compile_commands.json compile_commands.json
```

Works with VSCode (clangd extension), Neovim (nvim-lspconfig), Emacs (eglot), etc.

## API Reference

### WebSocket Endpoint: `/ws`

Real-time process state updates at 1 Hz.

**Server → Client:**
```json
{
  "type": "state",
  "data": {
    "time": 1234.5,
    "level": 2.5,
    "setpoint": 3.0,
    "inlet_flow": 1.0,
    "outlet_flow": 1.0,
    "valve_position": 0.5,
    "error": -0.5
  }
}
```

**Client → Server (Examples):**
```json
{"type": "setpoint", "value": 3.0}
{"type": "pid", "Kc": 1.0, "tau_I": 10.0, "tau_D": 0.0}
{"type": "inlet_flow", "value": 1.2}
{"type": "inlet_mode", "mode": "brownian", "min": 0.8, "max": 1.2}
{"type": "reset"}
```

### REST Endpoints

```
GET /api/history?duration=3600     # Last hour of data (default: last hour)
GET /api/config                    # Current simulation configuration
POST /api/reset                    # Reset to initial conditions
```

## Process Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| Tank height | 5.0 | m |
| Tank area | 120.0 | m² |
| Tank volume | 600.0 | m³ |
| Valve coefficient (k_v) | 1.2649 | m^2.5/s |
| Steady-state level | 2.5 | m |
| Steady-state inlet flow | 1.0 | m³/s |

## Troubleshooting

### CMake FetchContent Issues

If `cmake -B build -S .` fails downloading dependencies:

```bash
# Clear CMake cache and try again
rm -rf build
cmake -B build -S .

# Or manually specify GSL location
cmake -B build -S . -DGSL_ROOT_DIR=/usr/local
```

### Build Errors

Ensure you have a C++17 capable compiler:

```bash
gcc --version  # Should be 9.0+
g++ -std=c++17 -v  # Verify C++17 support
```

### WebSocket Connection Issues

Check that the FastAPI backend is running on port 8000:

```bash
curl http://localhost:8000/api/config
```

If backend isn't running, start it:

```bash
python -m api.main
```

## References

- **Tank Dynamics Theory**: See `docs/TankDynamics.md`
- **Tennessee Eastman Process**: See `docs/Tennessee_Eastman_Process_Equations.md`
- **Complete Architecture Plan**: See `docs/plan.md`
- **Next Implementation Tasks**: See `docs/next.md`

## License

This project is provided for educational and personal use.

## Contributing

Follow the workflow defined in `CLAUDE.md` when contributing:

1. Read the relevant role prompt (`prompts/*.md`)
2. Follow role boundaries strictly
3. Commit after each completed task with descriptive message
4. Escalate to higher-tier Claude models when appropriate

---

**Last Updated:** 2026-01-28
**Current Status:** Phase 1 In Progress
**Next Review:** After Task 4 completion
