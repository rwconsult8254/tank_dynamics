import asyncio
import logging
import uuid
from collections import deque
from typing import Any

import numpy as np

import tank_sim

logger = logging.getLogger(__name__)

MAX_SESSIONS = 100


class SessionSimulation:
    """
    Per-WebSocket-connection simulation instance.
    Each session owns its own Simulator, history, inlet mode, and async loop.
    """

    def __init__(self, session_id: str, config: tank_sim.SimulatorConfig, websocket):
        self.session_id = session_id
        self.config = config
        self.websocket = websocket
        self.simulator: tank_sim.Simulator | None = None
        self.history: deque = deque(maxlen=7200)  # 2 hours at 1 Hz
        self.inlet_mode: str = "constant"
        self.inlet_mode_params: dict[str, float] = {
            "min": 0.8,
            "max": 1.2,
            "variance": 0.05,
        }
        self._task: asyncio.Task | None = None
        self._initialize()

    def _initialize(self):
        """Initialize the simulator with a fresh config clone."""
        try:
            self.simulator = tank_sim.Simulator(self.config)
            logger.info(f"Session {self.session_id}: simulator initialized")
        except Exception as e:
            logger.error(f"Session {self.session_id}: failed to initialize: {e}")
            raise

    def get_state(self) -> dict[str, Any]:
        """Get current simulation state snapshot."""
        if self.simulator is None:
            return {
                "time": 0.0,
                "tank_level": 0.0,
                "setpoint": 0.0,
                "inlet_flow": 0.0,
                "outlet_flow": 0.0,
                "valve_position": 0.0,
                "error": 0.0,
                "controller_output": 0.0,
            }

        try:
            state = self.simulator.get_state()
            tank_level = state[0]
            setpoint = self.simulator.get_setpoint(0)
            inlet_flow = self.simulator.get_inputs()[0]
            valve_position = self.simulator.get_inputs()[1]
            error = self.simulator.get_error(0)
            controller_output = self.simulator.get_controller_output(0)
            time = self.simulator.get_time()

            k_v = self.config.model_params.k_v
            outlet_flow = (
                k_v * valve_position * (tank_level**0.5) if tank_level > 0 else 0.0
            )

            return {
                "time": float(time),
                "tank_level": float(tank_level),
                "setpoint": float(setpoint),
                "inlet_flow": float(inlet_flow),
                "outlet_flow": float(outlet_flow),
                "valve_position": float(valve_position),
                "error": float(error),
                "controller_output": float(controller_output),
            }
        except Exception as e:
            logger.error(f"Session {self.session_id}: error getting state: {e}")
            return {
                "time": 0.0,
                "tank_level": 0.0,
                "setpoint": 0.0,
                "inlet_flow": 0.0,
                "outlet_flow": 0.0,
                "valve_position": 0.0,
                "error": 0.0,
                "controller_output": 0.0,
            }

    def step(self):
        """Advance simulation by one time step."""
        if self.simulator is None:
            return

        try:
            if self.inlet_mode == "brownian":
                current_inlet_flow = self.simulator.get_inputs()[0]
                new_inlet_flow = self.apply_brownian_inlet(current_inlet_flow)
                self.simulator.set_input(0, new_inlet_flow)

            self.simulator.step()
        except Exception as e:
            logger.error(f"Session {self.session_id}: error during step: {e}")

    def reset(self):
        """Reset simulation to initial conditions and clear history."""
        if self.simulator is None:
            return

        try:
            self.simulator.reset()
            self.history.clear()
            self.inlet_mode = "constant"
            self.inlet_mode_params = {
                "min": 0.8,
                "max": 1.2,
                "variance": 0.05,
            }
            logger.info(f"Session {self.session_id}: reset")
        except Exception as e:
            logger.error(f"Session {self.session_id}: error resetting: {e}")

    def set_setpoint(self, value: float):
        """Set the controller setpoint."""
        if self.simulator is None:
            return
        try:
            self.simulator.set_setpoint(0, value)
        except Exception as e:
            logger.error(f"Session {self.session_id}: error setting setpoint: {e}")

    def set_pid_gains(self, gains: tank_sim.PIDGains):
        """Set PID controller gains."""
        if self.simulator is None:
            return
        try:
            self.simulator.set_controller_gains(0, gains)
        except Exception as e:
            logger.error(f"Session {self.session_id}: error setting PID gains: {e}")

    def set_inlet_flow(self, value: float):
        """Set inlet flow rate."""
        if self.simulator is None:
            return
        try:
            self.simulator.set_input(0, value)
        except Exception as e:
            logger.error(f"Session {self.session_id}: error setting inlet flow: {e}")

    def set_inlet_mode(
        self, mode: str, min_flow: float, max_flow: float, variance: float = 0.05
    ):
        """Set inlet flow mode (constant or brownian)."""
        self.inlet_mode = mode
        self.inlet_mode_params = {
            "min": min_flow,
            "max": max_flow,
            "variance": variance,
        }

    def apply_brownian_inlet(self, current_flow: float) -> float:
        """Apply Brownian motion to inlet flow."""
        increment = np.random.normal(0.0, self.inlet_mode_params["variance"])
        new_flow = current_flow + increment
        min_flow = self.inlet_mode_params["min"]
        max_flow = self.inlet_mode_params["max"]
        new_flow = np.clip(new_flow, min_flow, max_flow)
        return float(new_flow)

    def get_history(self, duration: int = 3600) -> list[dict[str, Any]]:
        """Get historical data points."""
        duration = max(1, min(duration, 7200))
        num_entries = min(duration, len(self.history))
        if num_entries == 0:
            return []
        return list(self.history)[-num_entries:]

    async def simulation_loop(self):
        """Main simulation loop running at 1 Hz, sending state to this session's websocket."""
        logger.info(f"Session {self.session_id}: simulation loop started")
        try:
            while True:
                await asyncio.sleep(1.0)
                try:
                    self.step()
                    state = self.get_state()
                    self.history.append(state)
                    await self.websocket.send_json({"type": "state", "data": state})
                except Exception as e:
                    logger.error(
                        f"Session {self.session_id}: error in loop iteration: {e}"
                    )
        except asyncio.CancelledError:
            logger.info(f"Session {self.session_id}: simulation loop cancelled")
            raise

    def start(self):
        """Start the simulation loop as an asyncio task."""
        self._task = asyncio.create_task(self.simulation_loop())

    async def stop(self):
        """Stop the simulation loop."""
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            logger.info(f"Session {self.session_id}: stopped")


class SessionManager:
    """
    Manages per-connection simulation sessions.
    Created once at startup, holds shared config.
    """

    def __init__(self, config: tank_sim.SimulatorConfig):
        self.config = config
        self.sessions: dict[str, SessionSimulation] = {}

    def create_session(self, websocket) -> SessionSimulation:
        """Create a new session for a WebSocket connection."""
        if len(self.sessions) >= MAX_SESSIONS:
            raise RuntimeError(
                f"Maximum sessions ({MAX_SESSIONS}) reached, rejecting connection"
            )

        session_id = str(uuid.uuid4())
        session = SessionSimulation(session_id, self.config, websocket)
        self.sessions[session_id] = session
        session.start()
        logger.info(f"Session created: {session_id} (active: {len(self.sessions)})")
        return session

    async def destroy_session(self, session_id: str):
        """Stop and remove a session."""
        session = self.sessions.pop(session_id, None)
        if session is not None:
            await session.stop()
            logger.info(
                f"Session destroyed: {session_id} (active: {len(self.sessions)})"
            )

    @property
    def active_session_count(self) -> int:
        return len(self.sessions)
