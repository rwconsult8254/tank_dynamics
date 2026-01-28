

#ifndef TANK_SIM_TANK_MODEL_H
#define TANK_SIM_TANK_MODEL_H

#include <Eigen/Dense>
#include <cmath>

namespace tank_sim {

class TankModel {
public:
    struct Parameters {
        double area;          // Cross-sectional area in square meters
        double k_v;           // Valve coefficient in cubic meters per second
        double max_height;    // Maximum tank height in meters
    };

    explicit TankModel(const Parameters& params)
        : params_(params) {}

    Eigen::VectorXd derivatives(const Eigen::VectorXd& state, const Eigen::VectorXd& inputs) const {
        // Current tank level (meters)
        double h = state(0);

        // Inlet flow (cubic meters per second)
        double q_in = inputs(0);

        // Valve position (dimensionless, 0 to 1)
        double valve_position = inputs(1);

        // Calculate outlet flow
        double q_out = outletFlow(h, valve_position);

        // Compute derivative of tank level using material balance equation
        double dh_dt = (q_in - q_out) / params_.area;

        return Eigen::VectorXd::Constant(1, dh_dt);
    }

    double outletFlow(double h, double x) const {
        if (h <= 0.0) {
            return 0.0; // No flow if tank level is zero or negative
        }
        return params_.k_v * x * std::sqrt(h);
    }

private:
    Parameters params_;
};

}  // namespace tank_sim

#endif  // TANK_SIM_TANK_MODEL_H
