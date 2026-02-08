# api/simulation.py

import tank_sim


class SimulationManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SimulationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        self.config = config
        self.initialized = False
        self.simulator = None
        self.setpoint = None
        self.PID = None
        self.inlet_flow = None

    def initialize(self):
        self.simulator = tank_sim.Simulator(**self.config)
        self.initialized = True

    def get_state(self):
        # Return dummy data matching StateSnapshot model structure
        return {
            "current_level": 0.0,
            "target_level": 10.0,
            "flow_rate": 0.5,
            "error": 0.0,
        }

    def step(self):
        pass

    def reset(self):
        self.simulator.reset()


# Example usage in main.py would be:
# simulation_manager = SimulationManager(config)
# await simulation_manager.initialize()
# state = simulation_manager.get_state()
