"use client";

import React from "react";

interface PIDTuningPopoverProps {
  currentGains: { Kc: number; tau_I: number; tau_D: number };
  reverseActing: boolean;
  onGainsChange: (newGains: {
    Kc: number;
    tau_I: number;
    tau_D: number;
  }) => void;
  onReverseActingChange: (reverseActing: boolean) => void;
  onClose: () => void;
}

export default function PIDTuningPopover({
  currentGains,
  reverseActing,
  onGainsChange,
  onReverseActingChange,
  onClose,
}: PIDTuningPopoverProps) {
  const popoverRef = React.useRef<HTMLDivElement>(null);
  const [localKc, setLocalKc] = React.useState(currentGains.Kc);
  const [localTauI, setLocalTauI] = React.useState(currentGains.tau_I);
  const [localTauD, setLocalTauD] = React.useState(currentGains.tau_D);
  const [localReverse, setLocalReverse] = React.useState(reverseActing);
  const [errorMessage, setErrorMessage] = React.useState("");

  // Close on click outside
  React.useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        popoverRef.current &&
        !popoverRef.current.contains(e.target as Node)
      ) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  // Close on Escape
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const handleApply = () => {
    if (localKc < 0 || localTauI < 0 || localTauD < 0) {
      setErrorMessage("All values must be >= 0");
      return;
    }
    setErrorMessage("");
    const kcToSend = localReverse ? -localKc : localKc;
    onGainsChange({ Kc: kcToSend, tau_I: localTauI, tau_D: localTauD });
    onReverseActingChange(localReverse);
    onClose();
  };

  const inputStyle =
    "w-16 bg-gray-700 text-white border border-gray-600 rounded px-1 py-0.5 text-xs font-mono text-right focus:outline-none focus:ring-1 focus:ring-blue-500";
  const labelStyle = "text-xs text-gray-400 font-mono w-10";

  return (
    <div
      ref={popoverRef}
      className="fixed bg-gray-800 border border-gray-600 rounded-md shadow-lg p-3 z-50"
      style={{
        minWidth: "200px",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
      }}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-bold text-gray-300">PID Tuning</span>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-300 text-xs"
        >
          &#x2715;
        </button>
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center gap-2">
          <span className={labelStyle}>Kc</span>
          <input
            type="number"
            min="0"
            step="0.1"
            value={localKc}
            onChange={(e) => {
              const v = parseFloat(e.target.value);
              if (!isNaN(v)) setLocalKc(v);
            }}
            className={inputStyle}
          />
        </div>
        <div className="flex items-center gap-2">
          <span className={labelStyle}>Ti (s)</span>
          <input
            type="number"
            min="0"
            step="1"
            value={localTauI}
            onChange={(e) => {
              const v = parseFloat(e.target.value);
              if (!isNaN(v)) setLocalTauI(v);
            }}
            className={inputStyle}
          />
        </div>
        <div className="flex items-center gap-2">
          <span className={labelStyle}>Td (s)</span>
          <input
            type="number"
            min="0"
            step="0.1"
            value={localTauD}
            onChange={(e) => {
              const v = parseFloat(e.target.value);
              if (!isNaN(v)) setLocalTauD(v);
            }}
            className={inputStyle}
          />
        </div>
        <label className="flex items-center gap-1.5 cursor-pointer">
          <input
            type="checkbox"
            checked={localReverse}
            onChange={(e) => setLocalReverse(e.target.checked)}
            className="w-3 h-3 rounded border-gray-600 bg-gray-700 text-blue-500"
          />
          <span className="text-xs text-gray-400">Reverse acting</span>
        </label>
      </div>

      {errorMessage && (
        <div className="text-xs text-red-400 mt-1">{errorMessage}</div>
      )}

      <button
        onClick={handleApply}
        className="w-full mt-2 bg-green-700 hover:bg-green-600 text-white text-xs font-semibold py-1 px-2 rounded transition-colors"
      >
        Apply
      </button>
    </div>
  );
}
