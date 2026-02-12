"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { WebSocketClient, ConnectionStatus } from "../lib/websocket";
import { SimulationState } from "../lib/types";

/**
 * React hook that wraps the WebSocket client and integrates with React lifecycle.
 * Manages connection, state updates, and provides command methods.
 */
export function useWebSocket(): {
  state: SimulationState | null;
  connectionStatus: ConnectionStatus;
  error: string | null;
  setSetpoint: (value: number) => void;
  setPIDGains: (Kc: number, tau_I: number, tau_D: number) => void;
  setInletFlow: (value: number) => void;
  setInletMode: (
    mode: string,
    min: number,
    max: number,
    variance: number,
  ) => void;
  reconnect: () => void;
} {
  const [state, setState] = useState<SimulationState | null>(null);
  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatus>("disconnected");
  const [error, setError] = useState<string | null>(null);
  const clientRef = useRef<WebSocketClient | null>(null);

  // Effect: Initialize connection on mount, cleanup on unmount
  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
    const client = new WebSocketClient(url);
    clientRef.current = client;

    const unsubConnect = client.on("connect", () => {
      setConnectionStatus("connected");
      setError(null);
    });

    const unsubDisconnect = client.on("disconnect", () => {
      setConnectionStatus("disconnected");
    });

    const unsubError = client.on("error", () => {
      setConnectionStatus("error");
      setError("WebSocket connection error");
    });

    const unsubMessage = client.on("message", (data: unknown) => {
      const msg = data as { type?: string; data?: unknown };
      if (msg.type === "state" && msg.data) {
        setState(msg.data as SimulationState);
      } else if (msg.type === "error") {
        const errMsg = msg as { message?: string };
        setError(errMsg.message || "Server error");
      }
    });

    client.connect();

    return () => {
      unsubConnect();
      unsubDisconnect();
      unsubError();
      unsubMessage();
      client.disconnect();
    };
  }, []);

  const setSetpoint = useCallback((value: number) => {
    try {
      clientRef.current?.send({ type: "setpoint", value });
    } catch {
      setError("Failed to send setpoint command");
    }
  }, []);

  const setPIDGains = useCallback(
    (Kc: number, tau_I: number, tau_D: number) => {
      try {
        clientRef.current?.send({ type: "pid", Kc, tau_I, tau_D });
      } catch {
        setError("Failed to send PID gains command");
      }
    },
    [],
  );

  const setInletFlow = useCallback((value: number) => {
    try {
      clientRef.current?.send({ type: "inlet_flow", value });
    } catch {
      setError("Failed to send inlet flow command");
    }
  }, []);

  const setInletMode = useCallback(
    (mode: string, min: number, max: number, variance: number) => {
      try {
        clientRef.current?.send({
          type: "inlet_mode",
          mode,
          min,
          max,
          variance,
        });
      } catch {
        setError("Failed to send inlet mode command");
      }
    },
    [],
  );

  const reconnect = useCallback(() => {
    setError(null);
    clientRef.current?.connect();
  }, []);

  return {
    state,
    connectionStatus,
    error,
    setSetpoint,
    setPIDGains,
    setInletFlow,
    setInletMode,
    reconnect,
  };
}
