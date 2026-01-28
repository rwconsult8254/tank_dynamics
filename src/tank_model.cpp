
namespace tank_sim {

    #include "tank_model.h"

TankModel::TankModel(const Parameters& params)
    : area(params.area),
      valve_coefficient(params.valve_coefficient),
      max_height(params.max_height) {
}

Eigen::VectorXd TankModel::derivatives(
    const Eigen::VectorXd& state,
    const Eigen::VectorXd& inputs) const {
    double current_level = state(0);
    double inlet_flow = inputs(0);
    double valve_position = inputs(1);

    double outlet_flow = outletFlow(current_level, valve_position);
    double dh_dt = (inlet_flow - outlet_flow) / area;

    Eigen::VectorXd derivative(1);
    derivative << dh_dt;
    return derivative;
}

double TankModel::outletFlow(double level, double valve_position) const {
    if (level <= 0.0) {
        return 0.0;
    }
    return valve_coefficient * valve_position * std::sqrt(level);
}

}  // namespace tank_sim
