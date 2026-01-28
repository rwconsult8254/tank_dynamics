# Next Tasks - Tank Dynamics Simulator

## Current Phase: Phase 1 - C++ Simulation Core

**Status:** Starting from scratch. No implementation files exist yet.

**Progress:** 0% - Project structure only

---

## Task 1: Initialize C++ Project Structure and Build System

**Phase:** 1 - C++ Simulation Core
**Prerequisites:** None (first task)

### Files to Create

- Create `/home/roger/dev/tank_dynamics/CMakeLists.txt` at project root
- Create `/home/roger/dev/tank_dynamics/src/CMakeLists.txt`
- Create `/home/roger/dev/tank_dynamics/tests/CMakeLists.txt`
- Create directory structure: `src/`, `tests/`, `bindings/`

### Requirements

This task sets up the CMake build system that will compile the C++ simulation library and tests.

The root CMakeLists.txt file should:
- Specify minimum CMake version as 3.20 or higher
- Define the project name as "TankDynamics" with CXX language
- Set C++ standard to 17 with required enforcement
- Use CMake FetchContent to download and configure dependencies
- Add subdirectories for src, tests, and later bindings

Dependencies to fetch using FetchContent:
- **Eigen3**: Version 3.4.0 from GitLab (gitlab.com/libeigen/eigen)
- **GSL (GNU Scientific Library)**: Use find_package first, if not found provide instructions to install via system package manager
- **GoogleTest**: Version 1.14.0 from GitHub (google/googletest)

The src/CMakeLists.txt should:
- Define a library target named "tank_sim_core" 
- Initially this library target will have no source files listed (just specify it as an interface or header-only for now)
- Set include directories so headers can be found
- Link against Eigen3 and GSL libraries

The tests/CMakeLists.txt should:
- Enable CMake testing with enable_testing()
- Create an executable target for tests
- Initially create a placeholder test file that will be populated in Task 3
- Link the test executable against tank_sim_core, GoogleTest, and its main function
- Register tests with CTest using gtest_discover_tests() or add_test()

### Build Verification

After implementing:
- Running `cmake -B build -S .` from project root should succeed
- CMake should download Eigen and GoogleTest automatically
- If GSL is not found, CMake should give clear instructions to install it (on Ubuntu: libgsl-dev, on Arch: gsl)
- Running `cmake --build build` should compile successfully (even with no source files yet)
- The build directory should contain compiled GoogleTest libraries

### Edge Cases

- **GSL not installed:** Provide clear error message with installation instructions for common distros
- **Network issues during FetchContent:** CMake should cache downloads, retry may be needed
- **Compiler not C++17 capable:** CMake should fail with clear message about C++ standard requirement

### Acceptance Criteria

- [ ] CMakeLists.txt created at project root
- [ ] src/CMakeLists.txt created with library target definition
- [ ] tests/CMakeLists.txt created with test framework setup
- [ ] Directory structure created: src/, tests/, bindings/ (bindings can be empty for now)
- [ ] CMake configure succeeds: `cmake -B build -S .`
- [ ] Dependencies are fetched: Eigen3 and GoogleTest downloaded
- [ ] Build succeeds: `cmake --build build`
- [ ] No compilation errors (even with minimal/no source files)

---

## Task 2: Implement TankModel Class

**Phase:** 1 - C++ Simulation Core
**Prerequisites:** Task 1 (build system must be in place)

### Files to Create

- Create `/home/roger/dev/tank_dynamics/src/tank_model.h`
- Create `/home/roger/dev/tank_dynamics/src/tank_model.cpp`
- Update `/home/roger/dev/tank_dynamics/src/CMakeLists.txt` to include these source files in the tank_sim_core library

### Requirements

The TankModel class represents the physics of a liquid tank with inlet and outlet flows. This is a stateless model that computes derivatives for numerical integration.

#### tank_model.h specifications:

The header should define a class called TankModel within a namespace (suggest using "tank_sim" namespace for all classes).

The class needs a public nested structure called Parameters containing:
- A field for cross-sectional area in square meters (type: double)
- A field for valve coefficient in cubic meters per second (type: double)
- A field for maximum tank height in meters (type: double)

The class should have:
- A constructor that takes a const reference to Parameters
- A method for computing derivatives that accepts:
  - Current state vector (tank level in meters) as an Eigen vector
  - Input vector containing inlet flow (cubic meters per second) and valve position (zero to one) as an Eigen vector
  - Returns an Eigen vector containing the derivative of tank level (dh/dt in meters per second)
- A method for computing outlet flow that accepts:
  - Tank level in meters (type: double)
  - Valve position from zero to one (type: double)
  - Returns outlet flow in cubic meters per second (type: double)

Both methods should be declared const since the model is stateless.

#### tank_model.cpp specifications:

Implement the constructor to store the parameters in private member variables.

Implement the derivatives method using the material balance equation:
- Rate of change of level equals the difference between inlet and outlet flows divided by tank area
- Inlet flow is the first element of the inputs vector
- Valve position is the second element of the inputs vector
- Tank level is the first (and only) element of the state vector
- Call the outletFlow method to compute the outlet flow
- Return a single-element Eigen vector containing dh/dt

Implement the outletFlow method using the valve flow equation:
- Outlet flow equals valve coefficient times valve position times square root of tank level
- Use standard library sqrt function
- This represents a square-root relationship between head and flow

#### Physics and Mathematics

The tank material balance: `dh/dt = (q_in - q_out) / A`
where:
- h is tank level (meters)
- q_in is inlet volumetric flow (cubic meters per second)
- q_out is outlet volumetric flow (cubic meters per second)
- A is cross-sectional area (square meters)

The valve equation: `q_out = k_v * x * sqrt(h)`
where:
- k_v is the valve coefficient (1.2649 cubic meters per second per square meter per square root meter, from plan)
- x is valve position (dimensionless, zero to one)
- h is tank level (meters)

### Edge Cases

- **Zero tank level:** When h equals zero, sqrt(h) equals zero, so outlet flow is zero (physically correct - no head means no flow)
- **Zero valve position:** When x equals zero, outlet flow is zero (valve fully closed)
- **Negative tank level:** Model does not need to handle this - integration logic will prevent it, but computing sqrt of negative is undefined behavior so document assumption that h is non-negative
- **Valve position outside zero to one:** Document assumption that caller ensures valve position is clamped to valid range

### Verification

To verify this implementation without the integrator:
- Test steady state: if inlet flow is 1.0 cubic meters per second, valve is 0.5, and level is 2.5 meters, outlet flow should equal inlet flow and derivative should be zero
- Use the parameters from the plan: area equals 120.0, k_v equals 1.2649, max_height equals 5.0
- Calculated outlet flow: 1.2649 times 0.5 times sqrt(2.5) equals approximately 1.0

### Acceptance Criteria

- [ ] tank_model.h created in src/ directory with class declaration
- [ ] tank_model.cpp created in src/ directory with implementation
- [ ] Class uses Eigen VectorXd for state and derivative vectors
- [ ] Parameters struct contains area, k_v, and max_height
- [ ] Constructor accepts and stores parameters
- [ ] derivatives() method implements material balance equation
- [ ] outletFlow() method implements valve equation with square root
- [ ] Both methods are const (stateless model)
- [ ] Code uses tank_sim namespace
- [ ] src/CMakeLists.txt updated to compile these files into tank_sim_core library
- [ ] Build succeeds: `cmake --build build`
- [ ] No compilation errors or warnings

---

## Task 3: Write Unit Tests for TankModel

**Phase:** 1 - C++ Simulation Core
**Prerequisites:** Task 2 (TankModel must be implemented)

### Files to Create

- Create `/home/roger/dev/tank_dynamics/tests/test_tank_model.cpp`
- Update `/home/roger/dev/tank_dynamics/tests/CMakeLists.txt` to compile this test file

### Requirements

This task creates comprehensive unit tests for the TankModel class using GoogleTest framework.

The test file should include the necessary headers:
- GoogleTest headers (gtest/gtest.h)
- Eigen headers
- The tank_model.h header

Create a test fixture class (using GoogleTest TEST_F) or use simple TEST macros for independent tests.

#### Test Cases to Implement

**Test: Steady State Zero Derivative**
- Set up TankModel with parameters from the plan (area: 120.0, k_v: 1.2649, max_height: 5.0)
- Create state vector with level at 2.5 meters
- Create input vector with inlet flow at 1.0 cubic meters per second and valve at 0.5
- Call derivatives method
- Assert that the returned derivative is approximately zero (use EXPECT_NEAR with tolerance of 0.001)
- This verifies that at steady state, dh/dt equals zero

**Test: Positive Derivative When Inlet Exceeds Outlet**
- Set up TankModel with same parameters
- Create state vector with level at 2.5 meters
- Create input vector with inlet flow at 1.5 cubic meters per second and valve at 0.5
- Call derivatives method
- Assert that the returned derivative is positive (greater than zero)
- Calculate expected value: (1.5 minus outlet_flow) divided by 120.0
- Verify the derivative matches expected value within tolerance

**Test: Negative Derivative When Outlet Exceeds Inlet**
- Set up TankModel with same parameters
- Create state vector with level at 2.5 meters  
- Create input vector with inlet flow at 0.5 cubic meters per second and valve at 0.5
- Call derivatives method
- Assert that the returned derivative is negative (less than zero)
- This represents tank draining

**Test: Outlet Flow Calculation**
- Set up TankModel with same parameters
- Call outletFlow method with level at 2.5 meters and valve at 0.5
- Calculate expected flow: 1.2649 times 0.5 times sqrt(2.5)
- Assert that returned flow matches expected value (use EXPECT_NEAR with tolerance of 0.001)

**Test: Zero Outlet Flow When Valve Closed**
- Set up TankModel
- Call outletFlow method with any positive level and valve at 0.0
- Assert that returned flow is exactly zero

**Test: Zero Outlet Flow When Tank Empty**
- Set up TankModel
- Call outletFlow method with level at 0.0 and valve at any position
- Assert that returned flow is exactly zero

**Test: Full Valve Opening**
- Set up TankModel
- Call outletFlow with level at 5.0 meters (max height) and valve at 1.0 (fully open)
- Calculate expected maximum flow: 1.2649 times 1.0 times sqrt(5.0)
- Assert returned flow matches expected

### Test Execution

The tests should be discoverable by CTest. After implementation:
- Build the project: `cmake --build build`
- Run tests: `ctest --test-dir build` or `./build/tests/test_executable_name`
- All tests should pass

### Edge Cases

- **Numerical precision:** Use EXPECT_NEAR with appropriate tolerance (0.001 is reasonable for these scales)
- **Eigen vector dimensions:** Verify that state and input vectors have correct sizes
- **Negative values:** While not physically expected, verify sqrt doesn't cause issues with zero input

### Acceptance Criteria

- [ ] test_tank_model.cpp created in tests/ directory
- [ ] File includes GoogleTest and required headers
- [ ] Steady state test implemented and passes
- [ ] Positive derivative test implemented and passes
- [ ] Negative derivative test implemented and passes
- [ ] Outlet flow calculation test implemented and passes
- [ ] Valve closed test implemented and passes
- [ ] Empty tank test implemented and passes
- [ ] Full valve opening test implemented and passes
- [ ] tests/CMakeLists.txt updated to compile test file
- [ ] Build succeeds: `cmake --build build`
- [ ] All tests pass: `ctest --test-dir build --output-on-failure`

---

## Upcoming Work (After Task 3)

Once TankModel is implemented and tested, the next tasks will be:

4. Implement PIDController class (pid_controller.h/cpp)
5. Write unit tests for PIDController
6. Implement Stepper class wrapping GSL RK4 (stepper.h/cpp)
7. Write integration accuracy tests for Stepper
8. Implement Simulator orchestrator class (simulator.h/cpp)
9. Write comprehensive tests for Simulator
10. Create standalone executable to run simulation and verify dynamics

After Phase 1 is complete, we'll move to Phase 2 (Python bindings using pybind11).

---

*Generated: 2026-01-28*
*Senior Engineer: Claude (Sonnet)*
