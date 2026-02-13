import json
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import tank_sim

from .models import ConfigResponse
from .simulation import SessionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global session manager instance
session_manager: SessionManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown."""
    global session_manager
    try:
        config = tank_sim.create_default_config()
        session_manager = SessionManager(config)
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize session manager: {e}")
        raise

    yield

    # Shutdown: destroy all active sessions
    if session_manager is not None:
        for session_id in list(session_manager.sessions.keys()):
            await session_manager.destroy_session(session_id)
    logger.info("Application shutting down")


# Create FastAPI application
app = FastAPI(
    title="Tank Dynamics Simulator API",
    description="Real-time tank level control simulation with PID control",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS: configurable via CORS_ORIGINS env var (comma-separated), with dev defaults
_cors_env = os.getenv("CORS_ORIGINS", "")
cors_origins = (
    [o.strip() for o in _cors_env.split(",") if o.strip()]
    if _cors_env
    else [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# REST Endpoints — only shared/stateless ones remain
@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "ok",
        "active_sessions": session_manager.active_session_count
        if session_manager
        else 0,
    }


@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    """Get default simulation configuration."""
    try:
        if session_manager is None:
            return JSONResponse(
                status_code=500, content={"error": "Application not initialized"}
            )

        config = session_manager.config
        model_params = config.model_params
        controller = config.controllers[0]
        gains = controller.gains

        return {
            "tank_height": model_params.max_height,
            "tank_area": model_params.area,
            "valve_coefficient": model_params.k_v,
            "initial_level": config.initial_state[0],
            "initial_setpoint": controller.initial_setpoint,
            "pid_gains": {
                "Kc": gains.Kc,
                "tau_I": gains.tau_I,
                "tau_D": gains.tau_D,
            },
            "timestep": config.dt,
            "history_capacity": 7200,
            "history_size": 0,
        }
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# WebSocket endpoint — each connection gets its own simulation session
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time simulation.
    Each connection gets its own independent simulation instance.

    Sends:
    - {"type": "state", "data": {...}} — 1 Hz state updates
    - {"type": "history", "data": [...]} — response to history request
    - {"type": "error", "message": "..."} — error messages

    Receives:
    - {"type": "setpoint", "value": <float>}
    - {"type": "pid", "Kc": <float>, "tau_I": <float>, "tau_D": <float>}
    - {"type": "inlet_flow", "value": <float>}
    - {"type": "inlet_mode", "mode": <str>, "min": <float>, "max": <float>, "variance": <float>}
    - {"type": "reset"}
    - {"type": "history", "duration": <int>}
    """
    await websocket.accept()
    logger.info("Client connected to WebSocket")

    if session_manager is None:
        await websocket.send_json(
            {"type": "error", "message": "Application not initialized"}
        )
        await websocket.close()
        return

    # Create a session for this connection
    try:
        session = session_manager.create_session(websocket)
    except RuntimeError as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        await websocket.close()
        return

    try:
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "Invalid JSON format"}
                )
                continue
            except Exception:
                break

            try:
                msg_type = message.get("type")

                if msg_type == "setpoint":
                    value = message.get("value")
                    if value is None:
                        await websocket.send_json(
                            {"type": "error", "message": "Missing 'value' field"}
                        )
                    else:
                        session.set_setpoint(float(value))

                elif msg_type == "pid":
                    kc = message.get("Kc")
                    tau_i = message.get("tau_I")
                    tau_d = message.get("tau_D")
                    if any(x is None for x in [kc, tau_i, tau_d]):
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "Missing PID gain fields (Kc, tau_I, tau_D)",
                            }
                        )
                    else:
                        gains = tank_sim.PIDGains()
                        gains.Kc = float(kc)
                        gains.tau_I = float(tau_i)
                        gains.tau_D = float(tau_d)
                        session.set_pid_gains(gains)

                elif msg_type == "inlet_flow":
                    value = message.get("value")
                    if value is None:
                        await websocket.send_json(
                            {"type": "error", "message": "Missing 'value' field"}
                        )
                    else:
                        session.set_inlet_flow(float(value))

                elif msg_type == "inlet_mode":
                    mode = message.get("mode")
                    min_val = message.get("min")
                    max_val = message.get("max")
                    variance = message.get("variance", 0.05)
                    if any(x is None for x in [mode, min_val, max_val]):
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "Missing inlet mode fields (mode, min, max)",
                            }
                        )
                    else:
                        session.set_inlet_mode(
                            str(mode), float(min_val), float(max_val), float(variance)
                        )

                elif msg_type == "reset":
                    session.reset()

                elif msg_type == "history":
                    duration = message.get("duration", 3600)
                    try:
                        duration = int(duration)
                    except (ValueError, TypeError):
                        duration = 3600
                    history_data = session.get_history(duration)
                    await websocket.send_json({"type": "history", "data": history_data})

                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {msg_type}",
                        }
                    )

            except (ValueError, TypeError) as e:
                await websocket.send_json(
                    {"type": "error", "message": f"Invalid message format: {e}"}
                )
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json(
                    {"type": "error", "message": f"Error processing command: {e}"}
                )

    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await session_manager.destroy_session(session.session_id)
