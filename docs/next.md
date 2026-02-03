# Next Tasks - Tank Dynamics Simulator

## Current Phase: Phase 1 - C++ Simulation Core

**Status:** TankModel, PIDController, and Stepper classes implemented

**Progress:** 60% - Core components complete, need integration tests and orchestrator

**Recent Commits:**
- Task 1: Initialize C++ Project Structure and Build System ✓
- Task 2: Implement TankModel Class ✓
- Task 3: Write Unit Tests for TankModel ✓
- Task 4: Implement PIDController Class ✓
- Task 5: Write Unit Tests for PIDController ✓
- Task 6: Implement Stepper Class with GSL RK4 ✓

---

## Task 7: Write Integration Tests for Stepper

**Phase:** 1 - C++ Simulation Core
**Prerequisites:** Task 6 (Stepper must be implemented)

### Files to Create

- Create `/home/roger/dev/tank_dynamics/tests/test_stepper.cpp`
- Update `/home/roger/dev/tank_dynamics/tests/CMakeLists.txt` to include this test file

### Requirements

This task creates integration tests for the Stepper class that verify the numerical accuracy and correctness of the GSL RK4 integration. Unlike unit tests that verify individual methods, these tests verify that the integration produces mathematically correct results.

The test file should include the necessary headers:
- GoogleTest headers (gtest/gtest.h)
- The stepper.h header
- Eigen headers for vector operations
- Standard library headers for mathematical functions (cmath for exp, sin, cos, etc.)

#### Test Cases to Implement

**Test: Exponential Decay Accuracy**
- Use the simple ODE: dy over dt equals negative k times y, where k equals 1.0
- This has analytical solution: y at time t equals y0 times exp of negative k times t
- Set initial condition y0 equals 1.0 at time t equals 0.0
- Create a Stepper with state dimension 1 and input dimension 0 (no inputs needed for this test)
- Define a derivative function that returns a vector containing negative k times y
- Integrate from t equals 0 to t equals 1.0 using step size dt equals 0.1
- Call step method ten times in a loop
- Final state should equal exp of negative 1.0 which equals approximately 0.367879
- Assert the result matches the analytical solution within tolerance 0.0001
- This verifies basic integration correctness

**Test: Fourth Order Accuracy Verification**
- Use the same exponential decay ODE
- Integrate from t equals 0 to t equals 1.0 using two different step sizes:
  - First integration: dt equals 0.1 (10 steps)
  - Second integration: dt equals 0.05 (20 steps)
- Compute absolute error for each integration by comparing to analytical solution
- RK4 is fourth-order accurate, meaning error scales as dt to the power of 4
- Calculate the ratio of errors: error with dt equals 0.1 divided by error with dt equals 0.05
- Expected ratio should be approximately (0.1 divided by 0.05) to the power of 4 equals 16
- Assert ratio is between 12 and 20 (allowing some numerical noise)
- This verifies the order of accuracy of the RK4 method

**Test: Oscillatory System (Harmonic Oscillator)**
- Use the harmonic oscillator system: d2y over dt2 equals negative omega squared times y
- Rewrite as two first-order ODEs:
  - dy0 over dt equals y1 (velocity)
  - dy1 over dt equals negative omega squared times y0 (acceleration)
- Set omega equals 2 times pi (frequency of 1 Hz, period of 1 second)
- Initial conditions: y0 equals 1.0 (initial position), y1 equals 0.0 (starts at rest)
- Analytical solution: y0 at time t equals cos of omega times t, y1 at time t equals negative omega times sin of omega times t
- Create Stepper with state dimension 2 and input dimension 0
- Integrate for one full period (t equals 0 to t equals 1.0) using dt equals 0.01
- Call step one hundred times
- After one period, should return to initial state: y0 approximately 1.0, y1 approximately 0.0
- Assert y0 matches 1.0 within tolerance 0.001
- Assert y1 matches 0.0 within tolerance 0.01
- This verifies the stepper handles multi-dimensional systems and conserves energy in oscillatory systems

**Test: System with Inputs**
- Use a simple driven system: dy over dt equals u minus k times y
- This represents a first-order lag driven by input u
- Set k equals 1.0, initial state y equals 0.0, constant input u equals 1.0
- Analytical solution: y at time t equals u divided by k times (1 minus exp of negative k times t)
- For u equals 1.0 and k equals 1.0: y at time t equals 1 minus exp of negative t
- At t equals 1.0: y should equal 1 minus exp of negative 1 equals approximately 0.632121
- Create Stepper with state dimension 1 and input dimension 1
- Define derivative function that accepts state and input vectors
- Create input vector containing the value 1.0
- Integrate from t equals 0 to t equals 1.0 using dt equals 0.1
- Assert final state matches analytical solution within tolerance 0.0001
- This verifies the stepper correctly passes input vectors to the derivative function

**Test: Vector Dimension Validation**
- Create Stepper with state dimension 2 and input dimension 1
- Attempt to call step with state vector of size 1 (wrong size)
- This should throw std::runtime_error with message about dimension mismatch
- Use EXPECT_THROW macro with specific exception type
- Also test with input vector of wrong size
- This verifies runtime safety checks are working

**Test: Zero Step Size**
- Create Stepper with state dimension 1 and input dimension 0
- Call step with dt equals 0.0
- State should remain unchanged (no integration occurs)
- This verifies handling of edge case where no time advancement is requested

**Test: Negative Step Size**
- Create Stepper with state dimension 1 and input dimension 0
- Call step with dt equals negative 0.1 (backward integration)
- Verify that integration proceeds backward in time
- Use exponential decay: starting at y equals 1.0, going backward should give larger values
- This verifies the stepper can handle backward integration if needed

### Mathematical Background

**Runge-Kutta 4th Order Method:**

For ODE dy over dt equals f of t comma y, the RK4 update is:

```
k1 = f(t, y)
k2 = f(t + dt/2, y + dt*k1/2)
k3 = f(t + dt/2, y + dt*k2/2)
k4 = f(t + dt, y + dt*k3)
y_new = y + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
```

This achieves fourth-order accuracy: local error is O of dt to the fifth power, global error is O of dt to the fourth power.

**Why These Tests Matter:**

- Exponential decay: Simple test with known solution, catches basic integration errors
- Order verification: Proves the method is actually fourth-order, not just "working"
- Harmonic oscillator: Tests energy conservation and multi-dimensional systems
- Driven system: Verifies input handling which is critical for tank simulation
- Dimension validation: Prevents runtime errors in production code
- Edge cases: Ensures robustness for unusual but valid inputs

### Test Execution

After implementation:
- Update tests/CMakeLists.txt to include test_stepper.cpp
- Build the project: `cmake --build build`
- Run all tests: `./build/tests/test_tank_sim_core`
- All new tests should pass

### Verification Strategy

If any test fails:
- Exponential decay failure suggests basic integration error
- Order verification failure suggests wrong algorithm or GSL configuration
- Oscillator failure suggests accumulation of error or phase drift
- Input test failure suggests incorrect parameter passing to derivative function
- Dimension test failure suggests validation is not working

### Acceptance Criteria

- [ ] test_stepper.cpp created in tests/ directory
- [ ] File includes GoogleTest, Stepper, Eigen, and math headers
- [ ] Exponential decay test implemented and passes
- [ ] Fourth-order accuracy test implemented and passes
- [ ] Harmonic oscillator test implemented and passes
- [ ] System with inputs test implemented and passes
- [ ] Vector dimension validation test implemented and passes
- [ ] Zero step size test implemented and passes
- [ ] Negative step size test implemented and passes
- [ ] tests/CMakeLists.txt updated to compile test file
- [ ] Build succeeds: `cmake --build build`
- [ ] All tests pass: `./build/tests/test_tank_sim_core`
- [ ] Tests verify RK4 achieves fourth-order accuracy
- [ ] Tests cover both single and multi-dimensional systems

---

## Task 8: Implement Simulator Class (Orchestrator)

**Phase:** 1 - C++ Simulation Core
**Prerequisites:** Tasks 2, 4, 6 (TankModel, PIDController, Stepper must all exist)

### Files to Create

- Create `/home/roger/dev/tank_dynamics/src/simulator.h`
- Create `/home/roger/dev/tank_dynamics/src/simulator.cpp`
- Update `/home/roger/dev/tank_dynamics/src/CMakeLists.txt` to include these files

### Requirements

The Simulator class is the master orchestrator that brings together TankModel, PIDController, and Stepper into a complete working simulation. This class owns all the component instances and provides the high-level API that will be exposed to Python.

This is the most complex class in Phase 1 because it must coordinate the interactions between stateless physics (TankModel), stateful control (PIDController), and numerical integration (Stepper) while maintaining correct timing and data flow.

#### simulator.h specifications:

The header should define a class called Simulator within the tank_sim namespace.

The class needs several nested structures for configuration:

**ControllerConfig structure** containing:
- A Gains structure (from PIDController)
- Bias value (type: double) - the controller output when error is zero
- Minimum output limit (type: double) - typically 0.0 for valves
- Maximum output limit (type: double) - typically 1.0 for valves  
- Maximum integral accumulation (type: double) - prevents excessive windup
- Measured index (type: int) - which state variable this controller reads
- Output index (type: int) - which input this controller writes to
- Initial setpoint (type: double) - must match the steady-state value of measured variable

**Config structure** containing:
- TankModel Parameters structure (from TankModel)
- Vector of ControllerConfig (type: std::vector of ControllerConfig)
- Initial state vector (type: Eigen::VectorXd) - steady-state values for all state variables
- Initial inputs vector (type: Eigen::VectorXd) - steady-state values for all inputs
- Time step dt in seconds (type: double)

The class should have:

**Constructor** that accepts:
- A const reference to the Config structure
- Should validate that the configuration makes sense (state size, input size, controller indices)
- Should initialize all internal components
- Should set simulation time to zero

**Core simulation method called step** with no parameters:
- Advances simulation by one time step (dt)
- Must follow the correct order of operations (see Design Principle section below)
- Returns nothing (void)

**State getter methods:**
- Method called getTime that returns current simulation time (type: double)
- Method called getState that returns current state vector (type: Eigen::VectorXd)
- Method called getInputs that returns current input vector (type: Eigen::VectorXd)
- Method called getSetpoint that accepts controller index and returns its current setpoint (type: double)
- Method called getControllerOutput that accepts controller index and returns its current output (type: double)
- Method called getError that accepts controller index and returns current error (type: double)

**Operator control methods:**
- Method called setInput that accepts input index (int) and value (double) - allows operator to change any input directly
- Method called setSetpoint that accepts controller index (int) and setpoint value (double)
- Method called setControllerGains that accepts controller index (int) and Gains reference

**Utility method:**
- Method called reset with no parameters - returns simulation to initial conditions

All getter methods should be const. Control methods should be non-const.

#### simulator.cpp specifications:

The class should maintain private member variables for:
- The TankModel instance
- The Stepper instance  
- A vector of PIDController instances (one per controller)
- Current simulation time (type: double)
- Current state vector (type: Eigen::VectorXd)
- Current input vector (type: Eigen::VectorXd)
- Initial state vector (for reset functionality)
- Initial inputs vector (for reset functionality)
- Time step dt (type: double)
- Vector of setpoints (type: std::vector of double, one per controller)
- Vector of ControllerConfig (store configuration for each controller)

**Constructor implementation:**

Validate the configuration:
- Check that initial state and initial inputs have matching dimensions to what TankModel expects
- Check that all controller measured_index values are within bounds of state vector size
- Check that all controller output_index values are within bounds of input vector size
- Check that dt is positive and reasonable (perhaps between 0.001 and 10.0 seconds)
- Throw std::invalid_argument if validation fails

Initialize components:
- Construct TankModel with provided parameters
- Construct Stepper with state dimension equal to initial state size and input dimension equal to initial inputs size
- For each ControllerConfig, construct a PIDController with the specified gains and bias
- Store initial state and initial inputs for reset functionality
- Set current state to initial state
- Set current input to initial inputs
- Set simulation time to zero
- Store all setpoints from the ControllerConfig vector

**Step method implementation (CRITICAL ORDER OF OPERATIONS):**

This is the heart of the simulation. The order matters because it models the one-step delay of real digital control systems.

Step 1: Integrate the model forward
- Create a lambda or method that wraps TankModel's derivatives method to match Stepper's DerivativeFunc signature
- Call Stepper's step method with:
  - Current time
  - Time step dt
  - Current state vector
  - Current input vector (these are from the PREVIOUS timestep)
  - The derivative function wrapper
- Store the returned new state as the current state

Step 2: Advance simulation time
- Add dt to current time

Step 3: Update all controllers for NEXT step
- For each controller:
  - Read the measured variable from current state using measured_index
  - Calculate error as setpoint minus measured value
  - Calculate error derivative (for now, can use simple finite difference or pass zero - derivative calculation can be refined later)
  - Call controller's compute method with error, error_dot, and dt
  - Write the controller output to the inputs vector at output_index

This order ensures that:
- Controllers act on current measurements
- But their outputs only affect the NEXT integration step
- This models the inherent delay in digital control systems

**Getter methods implementation:**

- getTime: return current time
- getState: return copy of current state vector
- getInputs: return copy of current inputs vector
- getSetpoint: return setpoints at specified controller index (validate index)
- getControllerOutput: return inputs at the controller's output_index
- getError: return setpoint minus state at controller's measured_index

**Control methods implementation:**

- setInput: validate index is within bounds, then update inputs vector at specified index
- setSetpoint: validate controller index, update setpoints vector at that index
- setControllerGains: validate controller index, call setGains on that controller

**Reset method implementation:**

- Copy initial state to current state
- Copy initial inputs to current inputs
- Set simulation time back to zero
- Reset all controllers (clear integral states)
- Restore all setpoints to their initial values from ControllerConfig

#### Design Principle: Steady-State Initialization

The simulation MUST be initialized at steady state. This is enforced through the configuration:

At steady state:
- All derivatives equal zero
- All state variables equal their setpoints
- All controller outputs equal their bias values
- System is in equilibrium

The constructor should document this requirement clearly. If the configuration is not at steady state, the simulation will start with a transient that could be confusing or unrealistic.

For the tank system specifically:
- Initial tank level should equal setpoint (typically 2.5 m for 50% level)
- Initial inlet flow and outlet flow should be equal (typically 1.0 m³/s)
- Initial valve position should equal controller bias (typically 0.5)

#### Design Principle: State vs Inputs

State variables:
- Governed by differential equations
- Evolved through integration by the Stepper
- NEVER set directly (except during initialization or reset)
- Example: tank level h

Input variables:
- Fed INTO the differential equations
- Control the derivatives
- Can be changed at any time by controllers or operators
- Example: inlet flow q_in, valve position x

This separation is fundamental to process simulation architecture.

### Edge Cases

- **Controller index out of bounds:** Validate in all methods that accept controller_index
- **Input index out of bounds:** Validate in setInput
- **Multiple controllers writing to same input:** Document as allowed but potentially confusing
- **Controller reading a state that doesn't exist:** Caught during construction validation
- **Zero or negative dt:** Validate in constructor
- **Very large dt:** Could cause numerical instability - document reasonable range

### Verification

Before writing formal tests (Task 9), verify the implementation compiles and can be instantiated:

Create a simple test configuration:
- TankModel parameters: area equals 120.0, k_v equals 1.2649, max_height equals 5.0
- Single controller controlling valve position based on tank level
- Initial state: level equals 2.5 m
- Initial inputs: q_in equals 1.0, x equals 0.5
- Time step: dt equals 1.0 second

Verify it compiles and runs without crashing:
- Construct Simulator with this config
- Call step a few times
- Call getters to retrieve state
- Verify no segfaults or exceptions

### Acceptance Criteria

- [ ] simulator.h created in src/ directory
- [ ] simulator.cpp created in src/ directory
- [ ] ControllerConfig nested structure defined with all required fields
- [ ] Config nested structure defined with all required fields
- [ ] Constructor validates configuration and throws on invalid input
- [ ] Constructor initializes TankModel, Stepper, and all PIDControllers
- [ ] step() method implements correct order of operations
- [ ] step() integrates model, advances time, then updates controllers
- [ ] getTime() returns current simulation time
- [ ] getState() returns current state vector
- [ ] getInputs() returns current inputs vector
- [ ] getSetpoint() returns setpoint for specified controller
- [ ] getControllerOutput() returns output for specified controller
- [ ] getError() returns error for specified controller
- [ ] setInput() allows changing input values
- [ ] setSetpoint() allows changing controller setpoint
- [ ] setControllerGains() allows retuning controllers
- [ ] reset() returns simulation to initial conditions
- [ ] All index accesses are bounds-checked
- [ ] Code uses tank_sim namespace
- [ ] Code includes detailed comments explaining order of operations
- [ ] src/CMakeLists.txt updated to compile these files
- [ ] Build succeeds: `cmake --build build`
- [ ] No compilation errors, warnings, or linker errors

---

## Task 9: Write Comprehensive Tests for Simulator

**Phase:** 1 - C++ Simulation Core
**Prerequisites:** Task 8 (Simulator must be implemented)

### Files to Create

- Create `/home/roger/dev/tank_dynamics/tests/test_simulator.cpp`
- Update `/home/roger/dev/tank_dynamics/tests/CMakeLists.txt` to include this test file

### Requirements

This task creates comprehensive integration tests for the Simulator class. These tests verify that the complete system behaves correctly: physics model, controller, and integration working together.

These are the most important tests in Phase 1 because they validate that the entire simulation system produces physically reasonable and correct behavior.

#### Test Cases to Implement

**Test: Constructor Validation**
- Attempt to create Simulator with invalid configurations:
  - Empty state vector
  - Empty inputs vector
  - Negative dt
  - Zero dt
  - Controller measured_index out of bounds (larger than state size)
  - Controller output_index out of bounds (larger than input size)
- Each should throw std::invalid_argument with descriptive message
- Use EXPECT_THROW with specific exception type

**Test: Steady State Remains Steady**
- Create Simulator with steady-state configuration:
  - Tank level at 2.5 m (50% of 5 m height)
  - Inlet flow 1.0 m³/s
  - Outlet valve at 0.5 (50% open)
  - Controller setpoint at 2.5 m
  - PID gains: Kc equals 1.0, tau_I equals 10.0, tau_D equals 0.0
- Run simulation for 100 steps (100 seconds at dt equals 1.0)
- At each step, verify:
  - Tank level remains at 2.5 m (within tolerance 0.01)
  - Inlet flow remains at 1.0 m³/s
  - Valve position remains at 0.5 (within tolerance 0.01)
  - Controller output remains near bias (within tolerance 0.01)
- This verifies initialization at steady state and numerical stability

**Test: Step Response - Level Increase**
- Initialize at steady state (level 2.5 m, setpoint 2.5 m)
- Change setpoint to 3.0 m (increase by 0.5 m)
- Run simulation for 200 steps
- Verify expected behavior:
  - Tank level should start increasing from 2.5 m
  - Valve should close (output decrease) to reduce outlet flow
  - Level should approach 3.0 m asymptotically
  - After 200 seconds, level should be close to 3.0 m (within 0.1 m)
  - No overshoot expected with these PID gains
- This verifies setpoint tracking and controller response

**Test: Step Response - Level Decrease**
- Initialize at steady state (level 2.5 m, setpoint 2.5 m)
- Change setpoint to 2.0 m (decrease by 0.5 m)
- Run simulation for 200 steps
- Verify expected behavior:
  - Tank level should start decreasing from 2.5 m
  - Valve should open (output increase) to increase outlet flow
  - Level should approach 2.0 m asymptotically
  - After 200 seconds, level should be close to 2.0 m (within 0.1 m)
- This verifies bidirectional control

**Test: Disturbance Rejection**
- Initialize at steady state (level 2.5 m, setpoint 2.5 m)
- At t equals 50 seconds, change inlet flow from 1.0 to 1.2 m³/s (step disturbance)
- Continue simulation for 200 more steps
- Verify:
  - Level will initially rise due to increased inlet
  - Controller should adjust valve to compensate
  - Level should return to setpoint 2.5 m
  - System should reach new steady state with different valve position
  - After 200 seconds, level should be back at setpoint (within 0.1 m)
- This verifies disturbance rejection capability

**Test: Controller Saturation and Recovery**
- Initialize at steady state
- Set setpoint to 4.5 m (very high, near maximum)
- Run simulation for 300 steps
- Verify:
  - Valve should saturate at 0.0 (fully closed) during initial response
  - Level should rise but more slowly than if valve could go negative
  - Anti-windup should prevent integral from growing excessively
  - Eventually level should approach 4.5 m
- Check that integral state is reasonable (not huge) using getControllerOutput

**Test: Reset Functionality**
- Create Simulator at steady state
- Run simulation for 50 steps
- Change setpoint to 3.5 m
- Run another 50 steps (system now in transient)
- Call reset()
- Verify:
  - Time is back to zero
  - State is back to initial state (level 2.5 m)
  - Inputs are back to initial inputs
  - Setpoint is back to initial value (2.5 m)
  - Controllers are reset (integral states zero)
- Run simulation again and verify behavior is identical to first run

**Test: Dynamic Retuning**
- Initialize at steady state
- Run for 50 steps
- Change PID gains to more aggressive values (higher Kc)
- Change setpoint
- Continue running
- Verify that system responds with new dynamics (faster response, possible overshoot)
- This verifies setControllerGains works during operation

**Test: Multiple Controllers (if applicable)**
- If the configuration supports multiple controllers, create a system with two controllers
- Verify both controllers operate independently
- Verify each controller writes to its correct output
- Verify each controller reads from its correct measured variable

**Test: Time Advancement**
- Create Simulator with dt equals 1.0
- Verify initial time is 0.0
- Call step() once, verify time is 1.0
- Call step() 9 more times, verify time is 10.0
- This verifies time tracking is correct

**Test: Getter Methods**
- Create Simulator
- Run a few steps
- Call all getter methods and verify:
  - getState() returns vector of correct size
  - getInputs() returns vector of correct size
  - getSetpoint() returns the correct setpoint value
  - getControllerOutput() returns value between 0 and 1
  - getError() returns setpoint minus measured value
  - getTime() returns positive value after steps

### Test Execution

After implementation:
- Update tests/CMakeLists.txt to include test_simulator.cpp
- Build the project: `cmake --build build`
- Run all tests: `./build/tests/test_tank_sim_core`
- All tests should pass

### Physical Intuition

These tests verify physically reasonable behavior:

- Steady state test: If nothing changes, tank should not drift
- Step response tests: Increasing setpoint should close valve, decreasing should open valve
- Disturbance rejection: Controller should counteract flow changes
- Saturation test: System should handle limits gracefully
- Reset test: Should be able to re-run experiments

If any test fails, it usually indicates:
- Wrong sign in control action (valve moving wrong direction)
- Incorrect order of operations in step method
- Wrong initial conditions (not at steady state)
- Numerical instability (dt too large)

### Acceptance Criteria

- [ ] test_simulator.cpp created in tests/ directory
- [ ] Constructor validation test implemented and passes
- [ ] Steady state test implemented and passes
- [ ] Step response increase test implemented and passes
- [ ] Step response decrease test implemented and passes
- [ ] Disturbance rejection test implemented and passes
- [ ] Controller saturation test implemented and passes
- [ ] Reset functionality test implemented and passes
- [ ] Dynamic retuning test implemented and passes
- [ ] Time advancement test implemented and passes
- [ ] Getter methods test implemented and passes
- [ ] All tests include clear comments explaining expected behavior
- [ ] tests/CMakeLists.txt updated to compile test file
- [ ] Build succeeds: `cmake --build build`
- [ ] All tests pass: `./build/tests/test_tank_sim_core`
- [ ] Tests verify physically realistic behavior

---

## Upcoming Work (After Task 9)

Once the Simulator is fully tested, Phase 1 (C++ Simulation Core) will be complete. The next major phase will be:

**Phase 2: Python Bindings**

Tasks will include:
10. Create pybind11 binding module structure
11. Wrap Simulator class for Python access
12. Convert between C++ Eigen vectors and NumPy arrays
13. Write Python tests using pytest
14. Create simple Python demonstration script

After Phase 2, we'll move to Phase 3: FastAPI backend for real-time web API.

---

## Notes

**Phase 1 Completion Criteria:**

Before moving to Phase 2, verify:
- All C++ classes implemented (TankModel, PIDController, Stepper, Simulator)
- All unit tests pass
- Simulator produces physically realistic behavior
- Code is well-documented with comments
- Build system works reliably
- No memory leaks (can verify with valgrind)

**Testing Philosophy:**

The test progression follows a pattern:
- Unit tests: Individual components in isolation (TankModel, PIDController)
- Integration tests: Components working together (Stepper with analytical solutions)
- System tests: Full simulation behavior (Simulator with realistic scenarios)

This ensures that when something fails, we can identify which layer has the problem.

**Next Phase Preview:**

The Python bindings will expose the Simulator class to Python with a pythonic interface:

```python
import tank_sim

config = {
    'model_params': {'area': 120.0, 'k_v': 1.2649, 'max_height': 5.0},
    'controllers': [...],
    'initial_state': [2.5],
    'initial_inputs': [1.0, 0.5],
    'dt': 1.0
}

sim = tank_sim.Simulator(config)
sim.step()
state = sim.get_state()  # Returns NumPy array
```

This will enable the FastAPI backend to orchestrate the simulation in real-time.

---

*Generated: 2026-02-03*
*Senior Engineer: Claude (Sonnet)*
