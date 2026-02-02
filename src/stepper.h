#pragma once

#include <Eigen/Dense>
#include <cstddef>
#include <functional>
#include <gsl/gsl_odeiv2.h>
#include <gsl/gsl_errno.h>


namespace tank_sim {
// ... rest of class

class Stepper {
public:
  // Class members and methods go here
  using DerivativeFunc = std::function<Eigen::VectorXd(
      double, const Eigen::VectorXd &, const Eigen::VectorXd &)>;

public:
  // Constructor that accepts the state dimension
  Stepper(size_t state_dimension);

  // Destructor to free GSL resources
  ~Stepper();

  // Delete copy constructor and copy assignment (Stepper cannot be copied)
  Stepper(const Stepper &) = delete;
  Stepper &operator=(const Stepper &) = delete;

  // Method to advance the state by one time step using the given derivative
  // function
  Eigen::VectorXd step(double t, double dt, const Eigen::VectorXd &state,
                       const Eigen::VectorXd &input, DerivativeFunc deriv_func);

private:
  gsl_odeiv2_step *stepper_;
  size_t state_dimension_;
};
} // namespace tank_sim
