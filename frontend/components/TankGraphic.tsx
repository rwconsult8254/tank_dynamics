"use client";

/**
 * TankGraphic component renders an SVG representation of a tank with animated liquid level.
 * Displays tank outline, liquid fill, scale markings, and setpoint indicator for SCADA interface.
 */

interface TankGraphicProps {
  level: number;
  setpoint: number;
  maxHeight: number;
  inletFlow: number;
  outletFlow: number;
}

export default function TankGraphic({
  level,
  setpoint,
  maxHeight,
  inletFlow,
  outletFlow,
}: TankGraphicProps) {
  // Calculate percentage of tank filled
  const levelPercentage = (level / maxHeight) * 100;
  const setpointPercentage = (setpoint / maxHeight) * 100;

  // SVG dimensions (viewBox coordinates)
  const viewBoxWidth = 400;
  const viewBoxHeight = 600;

  // Tank dimensions
  const tankLeft = 100;
  const tankTop = 80;
  const tankWidth = 200;
  const tankHeight = 400;
  const tankRight = tankLeft + tankWidth;
  const tankBottom = tankTop + tankHeight;

  // Calculate liquid fill height
  const liquidHeight = (levelPercentage / 100) * tankHeight;
  const liquidTop = tankBottom - liquidHeight;

  // Scale marks: 0, 1, 2, 3, 4, 5 meters
  const scaleMarks = [0, 1, 2, 3, 4, 5];
  const markSpacing = tankHeight / maxHeight;

  // Flow indicator colors
  const inletColor = inletFlow > 0 ? "#3b82f6" : "#6b7280";
  const outletColor = outletFlow > 0 ? "#3b82f6" : "#6b7280";
  const inletMarker =
    inletFlow > 0 ? "url(#arrowhead-blue)" : "url(#arrowhead-gray)";
  const outletMarker =
    outletFlow > 0 ? "url(#arrowhead-blue)" : "url(#arrowhead-gray)";

  return (
    <div className="flex items-center justify-center w-full h-full bg-gray-900 rounded-lg p-4">
      <svg
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
        className="w-full max-w-md aspect-auto"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Arrow marker definitions */}
        <defs>
          <marker
            id="arrowhead-blue"
            markerWidth="10"
            markerHeight="10"
            refX="5"
            refY="5"
            orient="auto"
          >
            <polygon points="0 0, 10 5, 0 10" fill="#3b82f6" />
          </marker>
          <marker
            id="arrowhead-gray"
            markerWidth="10"
            markerHeight="10"
            refX="5"
            refY="5"
            orient="auto"
          >
            <polygon points="0 0, 10 5, 0 10" fill="#6b7280" />
          </marker>
        </defs>

        {/* Scale marks on left side */}
        {scaleMarks.map((mark) => {
          const y = tankBottom - mark * markSpacing;
          return (
            <g key={`mark-${mark}`}>
              {/* Horizontal scale line */}
              <line
                x1={tankLeft - 15}
                y1={y}
                x2={tankLeft - 5}
                y2={y}
                stroke="#9ca3af"
                strokeWidth="2"
              />
              {/* Scale label */}
              <text
                x={tankLeft - 25}
                y={y + 5}
                fontSize="14"
                fill="#d1d5db"
                textAnchor="end"
                fontFamily="monospace"
              >
                {mark}m
              </text>
            </g>
          );
        })}

        {/* Tank outline */}
        <rect
          x={tankLeft}
          y={tankTop}
          width={tankWidth}
          height={tankHeight}
          stroke="#4b5563"
          fill="none"
          strokeWidth="3"
        />

        {/* Liquid fill */}
        <rect
          x={tankLeft}
          y={liquidTop}
          width={tankWidth}
          height={liquidHeight}
          fill="#3b82f6"
          className="transition-all duration-500"
        />

        {/* Setpoint line (horizontal dashed line) */}
        <line
          x1={tankLeft}
          y1={tankBottom - setpointPercentage * (tankHeight / 100)}
          x2={tankRight}
          y2={tankBottom - setpointPercentage * (tankHeight / 100)}
          stroke="#ef4444"
          strokeWidth="2"
          strokeDasharray="5,5"
        />

        {/* Inlet flow indicator arrow */}
        <line
          x1={57.5}
          y1={35}
          x2={57.5}
          y2={50}
          stroke={inletColor}
          strokeWidth="2"
          markerEnd={inletMarker}
          className={inletFlow > 0 ? "animate-pulse" : ""}
        />

        {/* Inlet flow label */}
        <text
          x={57.5}
          y={25}
          fontSize="14"
          fill="#d1d5db"
          textAnchor="middle"
          fontFamily="monospace"
        >
          {inletFlow.toFixed(2)} m³/s
        </text>

        {/* Outlet flow indicator arrow */}
        <line
          x1={182.5}
          y1={480}
          x2={182.5}
          y2={530}
          stroke={outletColor}
          strokeWidth="2"
          markerEnd={outletMarker}
          className={outletFlow > 0 ? "animate-pulse" : ""}
        />

        {/* Outlet flow label */}
        <text
          x={182.5}
          y={565}
          fontSize="14"
          fill="#d1d5db"
          textAnchor="middle"
          fontFamily="monospace"
        >
          {outletFlow.toFixed(2)} m³/s
        </text>

        {/* Inlet pipe at top */}
        <g>
          {/* Horizontal inlet pipe */}
          <rect x="30" y="50" width="50" height="15" fill="#6b7280" />
          {/* Connection to tank */}
          <rect x={tankLeft - 5} y="50" width="10" height="15" fill="#6b7280" />
        </g>

        {/* Outlet pipe at bottom with valve symbol */}
        <g>
          {/* Vertical outlet pipe */}
          <rect
            x={tankLeft + 75}
            y={tankBottom}
            width="15"
            height="40"
            fill="#6b7280"
          />
          {/* Valve circle (simplified valve symbol) */}
          <circle
            cx={tankLeft + 82.5}
            cy={tankBottom + 60}
            r="12"
            fill="none"
            stroke="#6b7280"
            strokeWidth="2"
          />
          {/* Valve cross inside circle */}
          <line
            x1={tankLeft + 75}
            y1={tankBottom + 60}
            x2={tankLeft + 90}
            y2={tankBottom + 60}
            stroke="#6b7280"
            strokeWidth="2"
          />
        </g>
      </svg>
    </div>
  );
}
