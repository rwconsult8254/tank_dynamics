"use client";

import React from "react";
import { useSimulation } from "../app/providers";
import { ConnectionStatus } from "./ConnectionStatus";
import TankGraphic from "./TankGraphic";
import PIDTuningPopover from "./PIDTuningPopover";
import { formatTime } from "../lib/utils";

export function ProcessView() {
  const { state, setSetpoint, setPIDGains } = useSimulation();
  const [showPIDPopover, setShowPIDPopover] = React.useState(false);
  const [currentPIDGains, setCurrentPIDGains] = React.useState({
    Kc: 1.0,
    tau_I: 10.0,
    tau_D: 1.0,
  });
  const [reverseActing, setReverseActing] = React.useState(true);

  // Fetch PID gains from backend on mount
  React.useEffect(() => {
    const fetchPIDGains = async () => {
      try {
        const response = await fetch("/api/config");
        if (!response.ok) return;
        const data = await response.json();
        if (data.pid_gains) {
          const { Kc, tau_I, tau_D } = data.pid_gains;
          setCurrentPIDGains({ Kc: Math.abs(Kc), tau_I, tau_D });
          setReverseActing(Kc < 0);
        }
      } catch {
        // Keep defaults if fetch fails
      }
    };
    fetchPIDGains();
  }, []);

  const handlePIDChange = (newGains: {
    Kc: number;
    tau_I: number;
    tau_D: number;
  }) => {
    setPIDGains(newGains.Kc, newGains.tau_I, newGains.tau_D);
    setCurrentPIDGains({
      Kc: Math.abs(newGains.Kc),
      tau_I: newGains.tau_I,
      tau_D: newGains.tau_D,
    });
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Compact header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-bold text-white">Process</h2>
          {state && (
            <span className="text-xs font-mono text-gray-400">
              T: {formatTime(state.time)}
            </span>
          )}
        </div>
        <ConnectionStatus />
      </div>

      {/* Main content */}
      {state === null ? (
        <div className="flex-1 flex items-center justify-center">
          <p className="text-gray-400 text-center">
            Waiting for WebSocket connection...
          </p>
        </div>
      ) : (
        <div className="relative flex-1">
          <TankGraphic
            level={state.tank_level}
            setpoint={state.setpoint}
            maxHeight={5.0}
            inletFlow={state.inlet_flow}
            outletFlow={state.outlet_flow}
            valvePosition={state.valve_position}
            controllerOutput={state.controller_output}
            error={state.error}
            onSetpointChange={setSetpoint}
            onPIDPopoverToggle={() => setShowPIDPopover((prev) => !prev)}
          />

          {showPIDPopover && (
            <PIDTuningPopover
              currentGains={currentPIDGains}
              reverseActing={reverseActing}
              onGainsChange={handlePIDChange}
              onReverseActingChange={setReverseActing}
              onClose={() => setShowPIDPopover(false)}
            />
          )}
        </div>
      )}
    </div>
  );
}
