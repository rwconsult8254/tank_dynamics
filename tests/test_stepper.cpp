#include <gtest/gtest.h>
#include <cmath>
#include <Eigen/Dense>
#include "../src/stepper.h"

using namespace tank_sim;

// Test fixture for Stepper integration tests
class StepperTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Setup code run before each test
    }

    void TearDown() override {
        // Cleanup code run after each test
    }
};

// Placeholder test to verify framework is working
TEST_F(StepperTest, FrameworkSetup) {
    EXPECT_TRUE(true);
}

// Test: Exponential Decay Accuracy
TEST_F(StepperTest, ExponentialDecayAccuracy) {
    // ODE: dy/dt = -k*y with k = 1.0
    // Analytical solution: y(t) = y0 * exp(-k*t)
    const double k = 1.0;
    const double y0 = 1.0;
    const double dt = 0.1;
    const int num_steps = 10;
    const double final_time = 1.0;
    const double tolerance = 0.0001;

    // Create a Stepper with state dimension 1 and input dimension 1 (minimum)
    Stepper stepper(1, 1);

    // Initial state
    Eigen::VectorXd state(1);
    state(0) = y0;

    // Define the derivative function: dy/dt = -k*y
    auto derivative = [&](double t, const Eigen::VectorXd& y, const Eigen::VectorXd& u) -> Eigen::VectorXd {
        Eigen::VectorXd dy(1);
        dy(0) = -k * y(0);
        return dy;
    };

    // Integrate from t=0 to t=1.0 with step size dt=0.1
    double current_time = 0.0;
    for (int i = 0; i < num_steps; ++i) {
        state = stepper.step(current_time, dt, state, Eigen::VectorXd::Zero(1), derivative);
        current_time += dt;
    }

    // Analytical solution at t=1.0: y(1.0) = 1.0 * exp(-1.0)
    double expected = y0 * std::exp(-k * final_time);
    
    // Assert the result matches the analytical solution within tolerance
    EXPECT_NEAR(state(0), expected, tolerance);
}

// Test: Fourth Order Accuracy Verification
TEST_F(StepperTest, FourthOrderAccuracyVerification) {
    // ODE: dy/dt = -k*y with k = 1.0
    // Analytical solution: y(t) = y0 * exp(-k*t)
    const double k = 1.0;
    const double y0 = 1.0;
    const double final_time = 1.0;

    // Define the derivative function: dy/dt = -k*y
    auto derivative = [&](double t, const Eigen::VectorXd& y, const Eigen::VectorXd& u) -> Eigen::VectorXd {
        Eigen::VectorXd dy(1);
        dy(0) = -k * y(0);
        return dy;
    };

    // Analytical solution at t=1.0
    double expected = y0 * std::exp(-k * final_time);

    // First integration: dt = 0.1 (10 steps)
    const double dt_coarse = 0.1;
    const int steps_coarse = 10;
    Stepper stepper_coarse(1, 1);
    Eigen::VectorXd state_coarse(1);
    state_coarse(0) = y0;
    double time_coarse = 0.0;

    for (int i = 0; i < steps_coarse; ++i) {
        state_coarse = stepper_coarse.step(time_coarse, dt_coarse, state_coarse, Eigen::VectorXd::Zero(1), derivative);
        time_coarse += dt_coarse;
    }
    double error_coarse = std::abs(state_coarse(0) - expected);

    // Second integration: dt = 0.05 (20 steps)
    const double dt_fine = 0.05;
    const int steps_fine = 20;
    Stepper stepper_fine(1, 1);
    Eigen::VectorXd state_fine(1);
    state_fine(0) = y0;
    double time_fine = 0.0;

    for (int i = 0; i < steps_fine; ++i) {
        state_fine = stepper_fine.step(time_fine, dt_fine, state_fine, Eigen::VectorXd::Zero(1), derivative);
        time_fine += dt_fine;
    }
    double error_fine = std::abs(state_fine(0) - expected);

    // RK4 is fourth-order: error scales as dt^4
    // Expected ratio: (0.1/0.05)^4 = 2^4 = 16
    double error_ratio = error_coarse / error_fine;

    // Assert ratio is between 12 and 20 (allowing numerical noise)
    EXPECT_GT(error_ratio, 12.0) << "Error ratio " << error_ratio << " is below expected range for fourth-order method";
    EXPECT_LT(error_ratio, 20.0) << "Error ratio " << error_ratio << " is above expected range for fourth-order method";
}

// Test: Oscillatory System (Harmonic Oscillator)
TEST_F(StepperTest, OscillatorySystemHarmonicOscillator) {
    // Harmonic oscillator: d2y/dt2 = -omega^2 * y
    // Rewritten as two first-order ODEs:
    //   dy0/dt = y1 (velocity)
    //   dy1/dt = -omega^2 * y0 (acceleration)
    // where y0 is position and y1 is velocity
    const double omega = 2.0 * M_PI;  // frequency = 1 Hz, period = 1 second
    const double dt = 0.01;
    const int num_steps = 100;

    // Initial conditions: y0 = 1.0 (initial position), y1 = 0.0 (at rest)
    Eigen::VectorXd state(2);
    state(0) = 1.0;
    state(1) = 0.0;

    // Create stepper with state dimension 2 and input dimension 2
    // Note: Due to implementation details of the Stepper class, input_dimension
    // must equal state_dimension for proper operation.
    Stepper stepper(2, 2);

    // Define the derivative function for the harmonic oscillator
    auto derivative = [&](double t, const Eigen::VectorXd& y, const Eigen::VectorXd& u) -> Eigen::VectorXd {
        Eigen::VectorXd dy(2);
        dy(0) = y(1);                        // dy0/dt = y1 (velocity)
        dy(1) = -omega * omega * y(0);      // dy1/dt = -omega^2 * y0 (acceleration)
        return dy;
    };

    // Integrate for one full period (t = 0 to t = 1.0) using dt = 0.01
    double current_time = 0.0;
    for (int i = 0; i < num_steps; ++i) {
        state = stepper.step(current_time, dt, state, Eigen::VectorXd::Zero(2), derivative);
        current_time += dt;
    }

    // After one period, the system should return to initial state
    // Analytical solution: y0(t) = cos(omega * t), y1(t) = -omega * sin(omega * t)
    // At t = 1.0: y0(1.0) ≈ cos(2π) = 1.0, y1(1.0) ≈ -omega * sin(2π) = 0.0
    
    EXPECT_NEAR(state(0), 1.0, 0.001) << "Position should return to initial value after one period";
    EXPECT_NEAR(state(1), 0.0, 0.01) << "Velocity should return to initial value after one period";
}

// Test: System with Inputs
TEST_F(StepperTest, SystemWithInputs) {
    // Driven first-order system: dy/dt = u - k*y
    // This represents a first-order lag driven by input u
    // Analytical solution: y(t) = (u/k) * (1 - exp(-k*t))
    const double k = 1.0;
    const double u = 1.0;
    const double dt = 0.1;
    const int num_steps = 10;
    const double final_time = 1.0;
    const double tolerance = 0.0001;

    // Initial state
    Eigen::VectorXd state(1);
    state(0) = 0.0;

    // Create stepper with state dimension 1 and input dimension 1
    Stepper stepper(1, 1);

    // Input vector with constant value u = 1.0
    Eigen::VectorXd input(1);
    input(0) = u;

    // Define the derivative function: dy/dt = u - k*y
    auto derivative = [&](double t, const Eigen::VectorXd& y, const Eigen::VectorXd& u_vec) -> Eigen::VectorXd {
        Eigen::VectorXd dy(1);
        dy(0) = u_vec(0) - k * y(0);
        return dy;
    };

    // Integrate from t=0 to t=1.0 with step size dt=0.1
    double current_time = 0.0;
    for (int i = 0; i < num_steps; ++i) {
        state = stepper.step(current_time, dt, state, input, derivative);
        current_time += dt;
    }

    // Analytical solution at t=1.0: y(1.0) = (u/k) * (1 - exp(-k*t))
    // For u=1.0 and k=1.0: y(1.0) = 1.0 * (1 - exp(-1.0))
    double expected = (u / k) * (1.0 - std::exp(-k * final_time));
    
    // Assert the result matches the analytical solution within tolerance
    EXPECT_NEAR(state(0), expected, tolerance) << "State should match analytical solution for driven first-order system";
}

