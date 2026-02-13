"use client";

import { useEffect, useCallback } from "react";
import { useSimulation } from "../app/providers";
import { SimulationState } from "../lib/types";

const DEFAULT_DURATION = 3600;

/**
 * React hook that fetches historical simulation data via WebSocket.
 *
 * Requests history from the backend through the session's WebSocket connection.
 * Automatically re-requests when duration changes.
 *
 * @param durationSeconds - Number of seconds of history to fetch (1-7200, default 3600)
 * @returns Object with history data, loading state, error state, and refetch function
 */
export function useHistory(durationSeconds: number = DEFAULT_DURATION): {
  history: SimulationState[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
} {
  const { historyData, requestHistory, connectionStatus, error } =
    useSimulation();

  const refetch = useCallback(() => {
    if (connectionStatus === "connected") {
      requestHistory(durationSeconds);
    }
  }, [durationSeconds, connectionStatus, requestHistory]);

  // Request history when duration changes or connection is established
  useEffect(() => {
    if (connectionStatus === "connected") {
      requestHistory(durationSeconds);
    }
  }, [durationSeconds, connectionStatus, requestHistory]);

  return {
    history: historyData ?? [],
    loading: connectionStatus === "connected" && historyData === null,
    error,
    refetch,
  };
}
