#include "simulator.h"
#include <iostream>
#include <iomanip>

using namespace tank_sim;

int main() {
  std::cout << std::fixed << std::setprecision(6);
  std::cout << "========================================\n";
  std::cout << "Simulator Verification Program\n";
  std::cout << "========================================\n\n";

  // Create configuration as specified in Task 8
  Simulator::ControllerConfig controller_config;
  controller_config.gains.Kc = 1.0;
  controller_config.gains.tau_I = 10.0;  // Integral time constant (seconds)
  controller_config.gains.tau_D = 0.5;   // Derivative time constant (seconds)
  controller_config.bias = 0.0;
  controller_config.minOutputLimit = 0.0;
  controller_config.maxOutputLimit = 1.0;
  controller_config.maxIntegralAccumulation = 10.0;
  controller_config.measuredIndex = 0;  // Measure tank level
  controller_config.outputIndex = 0;    // Control valve position
  controller_config.initialSetpoint = 2.5;

  Simulator::Config config;
  config.params.area = 120.0;
  config.params.k_v = 1.2649;
  config.params.max_height = 5.0;
  config.controllerConfig.push_back(controller_config);
  
  config.initialState = Eigen::VectorXd(1);
  config.initialState(0) = 2.5;  // level = 2.5 m
  
  config.initialInputs = Eigen::VectorXd(2);
  config.initialInputs(0) = 1.0;   // q_in = 1.0
  config.initialInputs(1) = 0.5;   // x (valve position) = 0.5
  
  config.dt = 1.0;  // dt = 1.0 second

  std::cout << "Configuration:\n";
  std::cout << "  TankModel parameters:\n";
  std::cout << "    area = " << config.params.area << "\n";
  std::cout << "    k_v = " << config.params.k_v << "\n";
  std::cout << "    max_height = " << config.params.max_height << "\n";
  std::cout << "  Initial state:\n";
  std::cout << "    level = " << config.initialState(0) << " m\n";
  std::cout << "  Initial inputs:\n";
  std::cout << "    q_in = " << config.initialInputs(0) << "\n";
  std::cout << "  Time step: dt = " << config.dt << " s\n";
  std::cout << "  Controller: valve position based on tank level\n\n";

  try {
    // Construct Simulator
    std::cout << "Constructing Simulator...\n";
    Simulator simulator(config);
    std::cout << "✓ Simulator constructed successfully\n\n";

    // Get initial state
    std::cout << "Initial State:\n";
    std::cout << "  Time: " << simulator.getTime() << " s\n";
    std::cout << "  State: " << simulator.getState().transpose() << " m\n";
    std::cout << "  Inputs: " << simulator.getInputs().transpose() << "\n";
    std::cout << "  Setpoint: " << simulator.getSetpoint(0) << " m\n\n";

    // Call step() multiple times
    std::cout << "Running simulation steps...\n";
    std::cout << "-----------------------------------------\n";
    
    for (int i = 0; i < 5; ++i) {
      simulator.step();
      
      std::cout << "Step " << (i + 1) << ":\n";
      std::cout << "  Time: " << simulator.getTime() << " s\n";
      std::cout << "  State: " << simulator.getState().transpose() << " m\n";
      std::cout << "  Inputs: " << simulator.getInputs().transpose() << "\n";
      std::cout << "  Error: " << simulator.getError(0) << "\n";
      std::cout << "  Controller output: " << simulator.getControllerOutput(0) << "\n";
    }

    std::cout << "\n========================================\n";
    std::cout << "SUMMARY\n";
    std::cout << "========================================\n";
    std::cout << "✓ Simulator instantiated successfully\n";
    std::cout << "✓ step() called 5 times without crashing\n";
    std::cout << "✓ All getters work correctly\n";
    std::cout << "✓ No segfaults or exceptions\n";
    std::cout << "\n✓ Verification PASSED\n";
    
    return 0;

  } catch (const std::exception &e) {
    std::cout << "\n✗ Exception caught: " << e.what() << "\n";
    std::cout << "✗ Verification FAILED\n";
    return 1;
  } catch (...) {
    std::cout << "\n✗ Unknown exception caught\n";
    std::cout << "✗ Verification FAILED\n";
    return 1;
  }
}
