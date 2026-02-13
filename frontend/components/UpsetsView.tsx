"use client";

import { useSimulation } from "../app/providers";
import InletFlowControl from "./InletFlowControl";

export function UpsetsView() {
  const { state, setInletFlow, setInletMode } = useSimulation();

  const handleFlowChange = (value: number) => {
    setInletFlow(value);
  };

  const handleModeChange = (
    mode: "constant" | "brownian",
    config?: { min: number; max: number; variance: number },
  ) => {
    if (mode === "constant") {
      setInletMode("constant", 0, 0, 0);
    } else if (config) {
      setInletMode(mode, config.min, config.max, config.variance);
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white mb-1">
          Process Upsets
        </h2>
        <p className="text-sm text-gray-400">
          Configure disturbance scenarios for the simulation
        </p>
      </div>

      <div className="max-w-md">
        <InletFlowControl
          currentFlow={state?.inlet_flow ?? 1.0}
          onFlowChange={handleFlowChange}
          onModeChange={handleModeChange}
        />
      </div>
    </div>
  );
}
