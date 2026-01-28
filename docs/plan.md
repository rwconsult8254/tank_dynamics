# Project Plan: Tank Dynamics Simulator

## Executive Summary

A real-time tank level control simulator with a SCADA-style interface. The system models a tank with variable inlet flow and PID-controlled outlet valve, allowing operators to experiment with control parameters and observe process dynamics. Built with a C++ simulation backend (using GSL and Eigen), exposed via pybind11 to a FastAPI server, with a Next.js frontend featuring WebSocket-based real-time updates.

## Architecture Overview

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
                                 │ WebSocket
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Server (Python)                      │
│  - WebSocket endpoint for real-time data                        │
│  - REST endpoints for control actions                           │
│  - Simulation orchestration (1 Hz tick rate)                    │
│  - Data history buffer (ring buffer, ~2 hours)                  │
└────────────────────────────────┬────────────────────────────────┘
                                 │ pybind11
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                 C++ Simulation Library                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Tank Model  │  │ PID Control  │  │  RK4 Stepper (GSL)   │  │
│  │  - ODEs      │  │  - Error     │  │  - Fixed timestep    │  │
│  │  - Valve     │  │  - Integral  │  │  - State integration │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                           Eigen (vectors/matrices)              │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Decisions

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Simulation Core | C++17 | Performance, numerical precision, Tennessee Eastman style |
| ODE Solver | GNU Scientific Library (GSL) | Robust RK4 implementation, well-documented |
| Linear Algebra | Eigen3 | Header-only, fast, industry standard |
| Build System | CMake | Cross-platform, FetchContent for dependencies |
| C++/Python Binding | pybind11 | Mature, excellent C++ integration |
| API Server | FastAPI | Async support, WebSockets, Python ecosystem |
| Frontend Framework | Next.js 14 (App Router) | React-based, good DX, SSR capability |
| Real-time Transport | WebSockets | Bidirectional, low latency for 1 Hz updates |
| Charting | Recharts | React-native, good performance, simpler than Plotly for this use case |
| Styling | Tailwind CSS | Rapid UI development, dark theme support |
| C++ Testing | GoogleTest | Industry standard, good CMake integration |
| Python Testing | pytest | Standard Python testing |
| E2E Testing | Playwright | Modern, reliable, good Next.js integration |

**Note on Recharts vs Plotly:** While you've used Plotly before, Recharts integrates more naturally with React's component model and has lighter bundle size. For the relatively simple time-series plots needed here (level, flow, valve position), Recharts is sufficient. If you prefer Plotly, it's a straightforward substitution.

## Component Breakdown

### C++ Simulation Library (`libsim`)

The simulation follows the Tennessee Eastman architecture pattern: the process model only computes derivatives, while integration is handled by an external stepper. This separation makes testing easier and follows established process simulation conventions.

#### Class 1: TankModel

**Purpose:** Stateless physics model - computes derivatives given current state and inputs

**Responsibilities:**
- Compute tank material balance derivative: `dh/dt = (q_in - q_out) / A`
- Compute outlet flow from valve equation: `q_out = k_v * x * sqrt(h)`
- Pure function with no internal state

**Interface:**
```cpp
class TankModel {
public:
    struct Parameters {
        double area;        // Cross-sectional area (m²)
        double k_v;         // Valve coefficient (m^2.5/s)
        double max_height;  // Maximum tank height (m)
    };

    explicit TankModel(const Parameters& params);

    // Compute derivatives given state and inputs
    // state: [h] - tank level (m)
    // inputs: [q_in, x] - inlet flow (m³/s), valve position (0-1)
    // Returns: [dh/dt]
    Eigen::VectorXd derivatives(
        const Eigen::VectorXd& state,
        const Eigen::VectorXd& inputs
    ) const;

    // Compute outlet flow (algebraic equation, not ODE)
    double outletFlow(double h, double x) const;
};
```

#### Class 2: PIDController

**Purpose:** Computes valve position from level error. Has internal state for integral term.

**Responsibilities:**
- Track integral of error over time
- Compute PID output with saturation (0-1 for valve)
- Anti-windup when saturated

**Interface:**
```cpp
class PIDController {
public:
    struct Gains {
        double Kc;      // Controller gain
        double tau_I;   // Integral time (s), 0 = no integral
        double tau_D;   // Derivative time (s), 0 = no derivative
    };

    explicit PIDController(const Gains& gains, double bias = 0.5);

    // Compute valve position given error and derivative
    // Returns valve position clamped to [0, 1]
    double compute(double error, double error_dot, double dt);

    // Update tuning parameters
    void setGains(const Gains& gains);

    // Reset integral state
    void reset();

    // Get current integral state (for logging)
    double getIntegralState() const;
};
```

#### Class 3: Stepper

**Purpose:** Wraps GSL RK4 integrator. Advances state vector by calling model's derivative function.

**Responsibilities:**
- Configure GSL ODE stepper (RK4 fixed step)
- Call TankModel::derivatives() at intermediate points as required by RK4
- Return updated state vector

**Interface:**
```cpp
class Stepper {
public:
    // Function type matching what GSL expects
    using DerivativeFunc = std::function<Eigen::VectorXd(
        double t,
        const Eigen::VectorXd& state,
        const Eigen::VectorXd& inputs
    )>;

    explicit Stepper(size_t state_dim);
    ~Stepper();

    // Advance state by dt using RK4
    // derivative_func is called multiple times per step
    Eigen::VectorXd step(
        double t,
        double dt,
        const Eigen::VectorXd& state,
        const Eigen::VectorXd& inputs,
        DerivativeFunc derivative_func
    );
};
```

#### Class 4: Simulator

**Purpose:** Orchestrator that owns all components and exposes the public API.

**Responsibilities:**
- Own TankModel, PIDController, and Stepper instances
- Maintain current state vector and simulation time
- Coordinate stepping: get PID output, step model, update state
- Handle inlet flow modes (manual, Brownian)
- Expose API for pybind11 binding

**Interface:**
```cpp
class Simulator {
public:
    struct Config {
        TankModel::Parameters tank;
        PIDController::Gains pid;
        double initial_level;      // Initial tank level (m)
        double initial_setpoint;   // Initial setpoint (m)
        double initial_inlet_flow; // Initial inlet flow (m³/s)
    };

    explicit Simulator(const Config& config);

    // Advance simulation by dt seconds
    void step(double dt);

    // State getters
    double getTime() const;
    double getLevel() const;
    double getSetpoint() const;
    double getInletFlow() const;
    double getOutletFlow() const;
    double getValvePosition() const;
    double getError() const;

    // Get full state as struct (for Python binding)
    struct State {
        double time;
        double level;
        double setpoint;
        double inlet_flow;
        double outlet_flow;
        double valve_position;
        double error;
    };
    State getState() const;

    // Manipulated variable setters
    void setInletFlow(double q_in);
    void setSetpoint(double sp);
    void setPIDGains(double Kc, double tau_I, double tau_D);

    // Inlet flow modes
    enum class InletMode { MANUAL, BROWNIAN };
    void setInletMode(InletMode mode, double min = 0.8, double max = 1.2);

    // Reset to initial conditions
    void reset();
};
```

#### Key Parameters (calculated from requirements)

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Tank height | 5.0 m | Specified |
| Cross-sectional area | 120.0 m² | From fill time requirement |
| Tank volume | 600.0 m³ | height × area |
| Valve coefficient k_v | 1.2649 m^2.5/s | Steady-state at 50% level, 50% valve |
| Initial level | 2.5 m | 50% of height |
| Initial valve position | 0.5 | 50% open |
| Initial flows | 1.0 m³/s | Specified inlet, outlet matches at steady state |

### Component 2: Python Bindings (`tank_sim`)

**Purpose:** Expose C++ library to Python

**Responsibilities:**
- Wrap TankSimulator class via pybind11
- Convert between C++ types and Python/NumPy types
- Provide pythonic interface

**Interfaces:**
```python
import tank_sim

sim = tank_sim.TankSimulator(config)
sim.step(1.0)  # Advance 1 second
state = sim.get_state()  # Returns dict with all state variables
```

### Component 3: FastAPI Backend (`api/`)

**Purpose:** Web API and simulation orchestration

**Responsibilities:**
- Run simulation loop at 1 Hz (real-time)
- Broadcast state via WebSocket to connected clients
- Handle control commands (setpoint, PID tuning, inlet flow)
- Maintain ring buffer of last 2 hours of data (~7200 points)
- Provide REST endpoints for historical data and configuration

**Interfaces:**
```
WebSocket /ws
  -> Server sends: {"type": "state", "data": {...}} every 1s
  <- Client sends: {"type": "setpoint", "value": 3.0}
  <- Client sends: {"type": "pid", "Kc": 1.0, "tau_I": 10.0, "tau_D": 0.0}
  <- Client sends: {"type": "inlet_flow", "value": 1.2}
  <- Client sends: {"type": "inlet_mode", "mode": "brownian", "min": 0.8, "max": 1.2}

REST GET /api/history?duration=3600
  -> Returns last hour of data points

REST GET /api/config
  -> Returns current simulation configuration

REST POST /api/reset
  -> Resets simulation to initial steady state
```

### Component 4: Next.js Frontend (`frontend/`)

**Purpose:** SCADA-style user interface

**Responsibilities:**
- Display real-time process state (tank level, flows, valve position)
- Render tank visualization with animated level
- Provide controls for setpoint, PID parameters, inlet flow
- Display trend charts for process variables
- Manage WebSocket connection and reconnection

**Sub-components:**
1. **ProcessView** - Tank schematic, live values, controls
2. **TrendsView** - Time-series plots
3. **ControlPanel** - PID tuning, setpoint, inlet flow controls
4. **TankGraphic** - SVG tank with animated fill level

## Implementation Phases

### Phase 1: C++ Simulation Core
**Goals:** Working simulation engine with tests
**Deliverables:**
- CMakeLists.txt with FetchContent for Eigen, GSL, GoogleTest
- Tank model implementation (ODEs, valve, PID)
- RK4 integration using GSL
- Unit tests for all components
- Standalone test executable to verify dynamics

**Dependencies:** None

### Phase 2: Python Bindings
**Goals:** Simulation accessible from Python
**Deliverables:**
- pybind11 module wrapping TankSimulator
- Python package structure (`tank_sim/`)
- Python tests using pytest
- Simple Python script demonstrating usage

**Dependencies:** Phase 1

### Phase 3: FastAPI Backend
**Goals:** Real-time API server
**Deliverables:**
- FastAPI application with WebSocket support
- Simulation loop running at 1 Hz
- Ring buffer for 2-hour history
- REST endpoints for history and control
- API tests

**Dependencies:** Phase 2

### Phase 4: Next.js Frontend - Structure
**Goals:** Basic UI framework
**Deliverables:**
- Next.js project with App Router
- Tailwind CSS with dark theme
- Tab navigation (Process / Trends)
- WebSocket connection hook
- Basic layout and styling

**Dependencies:** Phase 3 (for testing, can start in parallel)

### Phase 5: Process View
**Goals:** SCADA-style process display
**Deliverables:**
- Tank SVG visualization with animated level
- Flow indicators (inlet, outlet)
- Valve position indicator
- Live value displays
- Control inputs (setpoint, inlet flow, PID parameters)

**Dependencies:** Phase 4

### Phase 6: Trends View
**Goals:** Historical trend charts
**Deliverables:**
- Level vs Setpoint chart
- Inlet Flow vs Outlet Flow chart
- Valve Position chart
- Time range selector
- Auto-scrolling with new data

**Dependencies:** Phase 4

### Phase 7: Integration and Polish
**Goals:** Complete, tested system
**Deliverables:**
- E2E tests with Playwright
- Error handling and reconnection logic
- Performance optimization
- Documentation updates

**Dependencies:** Phases 5, 6

## Project Structure

```
tank_dynamics/
├── CMakeLists.txt              # Top-level CMake
├── src/                        # C++ source
│   ├── CMakeLists.txt
│   ├── tank_model.h            # Class 1: Stateless derivative function
│   ├── tank_model.cpp
│   ├── pid_controller.h        # Class 2: PID with integral state
│   ├── pid_controller.cpp
│   ├── stepper.h               # Class 3: GSL RK4 wrapper
│   ├── stepper.cpp
│   ├── simulator.h             # Class 4: Orchestrator
│   └── simulator.cpp
├── bindings/                   # pybind11 bindings
│   ├── CMakeLists.txt
│   └── bindings.cpp
├── tests/                      # C++ tests
│   ├── CMakeLists.txt
│   ├── test_tank_model.cpp     # Test derivative calculations
│   ├── test_pid_controller.cpp # Test PID logic
│   ├── test_stepper.cpp        # Test integration accuracy
│   └── test_simulator.cpp      # Test full orchestration
├── api/                        # FastAPI backend
│   ├── __init__.py
│   ├── main.py
│   ├── simulation.py
│   ├── models.py
│   └── tests/
│       └── test_api.py
├── frontend/                   # Next.js frontend
│   ├── package.json
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── components/
│   ├── tailwind.config.js
│   └── tests/
│       └── e2e/
├── docs/
│   ├── specs.md
│   ├── plan.md
│   └── ...
└── scripts/
    └── run_dev.sh              # Start all services
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GSL integration complexity | Medium | Medium | Use CMake FetchContent; fallback to simpler Euler method if needed |
| WebSocket reliability | Low | Medium | Implement reconnection logic with exponential backoff |
| Real-time performance (1 Hz) | Low | Low | 1 Hz is easily achievable; profile if issues arise |
| pybind11 build issues | Medium | Medium | Pin versions; provide fallback Python simulation for frontend dev |
| Brownian motion inlet causing instability | Low | Medium | Implement rate limiting on random walk; clamp to safe bounds |

## Testing Strategy

### Unit Tests (C++ - GoogleTest)

**TankModel tests:**
- Verify `dh/dt = 0` at steady state (q_in = q_out)
- Verify `dh/dt > 0` when q_in > q_out
- Verify `dh/dt < 0` when q_in < q_out
- Verify outlet flow calculation: `q_out = k_v * x * sqrt(h)`
- Edge cases: h = 0, x = 0, x = 1

**PIDController tests:**
- Proportional only: output proportional to error
- Integral accumulation: output increases over time with constant error
- Derivative response: output responds to rate of change
- Saturation: output clamped to [0, 1]
- Anti-windup: integral doesn't wind up when saturated
- Reset: integral state clears

**Stepper tests:**
- Simple ODE with known solution (e.g., exponential decay)
- Verify 4th-order accuracy by comparing step sizes
- State dimension handling

**Simulator tests:**
- Steady-state: no change when at setpoint
- Step response: correct transient behavior
- Setpoint tracking: level follows setpoint changes
- Mode switching: Brownian inlet generates bounded random walk

### Unit Tests (Python - pytest)
- Binding functionality: ensure all methods accessible
- Type conversions: verify data passes correctly between C++/Python
- State consistency: run steps and verify state updates

### Integration Tests (pytest)
- API endpoints: test REST routes
- WebSocket: test connection, message format, command handling
- Simulation loop: verify timing and state updates

### E2E Tests (Playwright)
- UI renders correctly
- WebSocket connection established
- Controls update simulation
- Trends display data
- Tab navigation works

## Success Criteria

- [ ] Simulation runs in real-time (1 Hz) without drift
- [ ] Tank level responds correctly to setpoint changes
- [ ] PID controller stabilizes level at setpoint
- [ ] Inlet flow step changes cause expected transient response
- [ ] Brownian inlet mode produces realistic disturbances
- [ ] Frontend displays live process state
- [ ] Trend charts show 2 hours of history
- [ ] All unit tests pass
- [ ] E2E tests verify complete workflow
- [ ] System runs on Linux (primary), with potential for other platforms

## Next Steps

1. Initialize GitHub repository
2. Set up CMake project structure with FetchContent
3. Begin Phase 1: C++ Simulation Core

---

*Plan created: 2026-01-28*
*Architect: Claude (Opus)*
