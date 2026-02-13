"use client";

import React from "react";
import { formatLevel, formatFlowRate, formatValvePosition } from "../lib/utils";

interface TankGraphicProps {
  level: number;
  setpoint: number;
  maxHeight: number;
  inletFlow: number;
  outletFlow: number;
  valvePosition: number;
  controllerOutput: number;
  error: number;
  onSetpointChange: (value: number) => void;
  onPIDPopoverToggle: () => void;
}

export default function TankGraphic({
  level,
  setpoint,
  maxHeight,
  inletFlow,
  outletFlow,
  valvePosition,
  controllerOutput,
  error,
  onSetpointChange,
  onPIDPopoverToggle,
}: TankGraphicProps) {
  const [localSetpoint, setLocalSetpoint] = React.useState(setpoint.toFixed(1));
  const [isEditingSetpoint, setIsEditingSetpoint] = React.useState(false);

  // Sync local setpoint when not editing
  React.useEffect(() => {
    if (!isEditingSetpoint) {
      setLocalSetpoint(setpoint.toFixed(1));
    }
  }, [setpoint, isEditingSetpoint]);

  const handleSetpointSubmit = () => {
    const value = parseFloat(localSetpoint);
    if (!isNaN(value) && value >= 0 && value <= maxHeight) {
      onSetpointChange(Math.round(value * 10) / 10);
    } else {
      setLocalSetpoint(setpoint.toFixed(1));
    }
    setIsEditingSetpoint(false);
  };

  const handleSetpointKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSetpointSubmit();
    } else if (e.key === "Escape") {
      setLocalSetpoint(setpoint.toFixed(1));
      setIsEditingSetpoint(false);
    }
  };

  // Layout constants
  const viewBoxWidth = 800;
  const viewBoxHeight = 440;

  // Pipe styling
  const pipeColor = "#6b7280";
  const pipeWidth = 3;

  // Tank geometry
  const tankLeft = 300;
  const tankTop = 60;
  const tankWidth = 160;
  const tankHeight = 260;
  const tankRight = tankLeft + tankWidth;
  const tankBottom = tankTop + tankHeight;

  // Liquid fill
  const levelPct = Math.min(level / maxHeight, 1);
  const liquidHeight = levelPct * tankHeight;
  const liquidTop = tankBottom - liquidHeight;

  // Setpoint line
  const spPct = Math.min(setpoint / maxHeight, 1);
  const spY = tankBottom - spPct * tankHeight;

  // Scale marks
  const scaleMarks = [0, 1, 2, 3, 4, 5];
  const markSpacing = tankHeight / maxHeight;

  // Valve geometry (bow-tie)
  const valveX = 580;
  const valveY = 380;
  const valveSize = 14;

  // Tag box style
  const tagBg = "#1f2937";
  const tagBorder = "#4b5563";
  const tagText = "#d1d5db";
  const tagValue = "#e5e7eb";
  const tagFontSize = 11;
  const tagValueFontSize = 12;

  return (
    <div className="relative w-full h-full flex items-center justify-center bg-gray-900 rounded-lg">
      <svg
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* === PIPES === */}

        {/* Inlet pipe: left edge -> tank top-left */}
        <polyline
          points={`40,${tankTop + 30} ${tankLeft},${tankTop + 30}`}
          fill="none"
          stroke={pipeColor}
          strokeWidth={pipeWidth}
        />
        {/* Inlet pipe enters tank (short vertical drop inside) */}
        <line
          x1={tankLeft}
          y1={tankTop + 30}
          x2={tankLeft}
          y2={tankTop + 50}
          stroke={pipeColor}
          strokeWidth={pipeWidth}
        />

        {/* Outlet pipe: tank bottom -> down -> right to valve -> right to edge */}
        <polyline
          points={`${tankLeft + tankWidth / 2},${tankBottom} ${tankLeft + tankWidth / 2},${valveY} ${valveX - valveSize - 2},${valveY}`}
          fill="none"
          stroke={pipeColor}
          strokeWidth={pipeWidth}
        />
        {/* Pipe after valve to right edge */}
        <line
          x1={valveX + valveSize + 2}
          y1={valveY}
          x2={760}
          y2={valveY}
          stroke={pipeColor}
          strokeWidth={pipeWidth}
        />

        {/* === TANK === */}

        {/* Tank outline */}
        <rect
          x={tankLeft}
          y={tankTop}
          width={tankWidth}
          height={tankHeight}
          stroke="#9ca3af"
          fill="none"
          strokeWidth={2}
        />

        {/* Liquid fill */}
        <rect
          x={tankLeft + 1}
          y={liquidTop}
          width={tankWidth - 2}
          height={liquidHeight}
          fill="#3b82f6"
          opacity={0.6}
        />

        {/* Setpoint line (gray dashed - ISA-101: no red in normal operation) */}
        <line
          x1={tankLeft + 4}
          y1={spY}
          x2={tankRight - 4}
          y2={spY}
          stroke="#9ca3af"
          strokeWidth={1.5}
          strokeDasharray="6,3"
        />
        <text
          x={tankRight + 6}
          y={spY + 4}
          fontSize={10}
          fill="#9ca3af"
          fontFamily="monospace"
        >
          SP
        </text>

        {/* Scale marks on left side */}
        {scaleMarks.map((mark) => {
          const y = tankBottom - mark * markSpacing;
          return (
            <g key={`mark-${mark}`}>
              <line
                x1={tankLeft - 8}
                y1={y}
                x2={tankLeft - 2}
                y2={y}
                stroke="#6b7280"
                strokeWidth={1}
              />
              <text
                x={tankLeft - 12}
                y={y + 3}
                fontSize={9}
                fill="#6b7280"
                textAnchor="end"
                fontFamily="monospace"
              >
                {mark}
              </text>
            </g>
          );
        })}

        {/* === VALVE (ISA bow-tie symbol) === */}
        <g>
          {/* Left triangle */}
          <polygon
            points={`${valveX - valveSize},${valveY - valveSize} ${valveX},${valveY} ${valveX - valveSize},${valveY + valveSize}`}
            fill="none"
            stroke="#9ca3af"
            strokeWidth={1.5}
          />
          {/* Right triangle */}
          <polygon
            points={`${valveX + valveSize},${valveY - valveSize} ${valveX},${valveY} ${valveX + valveSize},${valveY + valveSize}`}
            fill="none"
            stroke="#9ca3af"
            strokeWidth={1.5}
          />
          {/* Actuator stem (line up from center) */}
          <line
            x1={valveX}
            y1={valveY - valveSize}
            x2={valveX}
            y2={valveY - valveSize - 12}
            stroke="#9ca3af"
            strokeWidth={1.5}
          />
          {/* Actuator box */}
          <rect
            x={valveX - 8}
            y={valveY - valveSize - 22}
            width={16}
            height={10}
            fill="none"
            stroke="#9ca3af"
            strokeWidth={1.5}
          />
        </g>

        {/* === INSTRUMENT TAGS === */}

        {/* FI-100: Inlet flow tag (near inlet pipe) */}
        <g>
          <rect
            x={100}
            y={tankTop + 2}
            width={100}
            height={36}
            rx={3}
            fill={tagBg}
            stroke={tagBorder}
            strokeWidth={1}
          />
          <text
            x={150}
            y={tankTop + 16}
            fontSize={tagFontSize}
            fill={tagText}
            textAnchor="middle"
            fontFamily="monospace"
          >
            FI-100
          </text>
          <text
            x={150}
            y={tankTop + 31}
            fontSize={tagValueFontSize}
            fill={tagValue}
            textAnchor="middle"
            fontFamily="monospace"
            fontWeight="bold"
          >
            {formatFlowRate(inletFlow)} m³/s
          </text>
        </g>

        {/* LI-100: Tank level tag (right of tank) */}
        <g>
          <rect
            x={tankRight + 30}
            y={tankTop + 20}
            width={100}
            height={36}
            rx={3}
            fill={tagBg}
            stroke={tagBorder}
            strokeWidth={1}
          />
          <text
            x={tankRight + 80}
            y={tankTop + 34}
            fontSize={tagFontSize}
            fill={tagText}
            textAnchor="middle"
            fontFamily="monospace"
          >
            LI-100
          </text>
          <text
            x={tankRight + 80}
            y={tankTop + 49}
            fontSize={tagValueFontSize}
            fill={tagValue}
            textAnchor="middle"
            fontFamily="monospace"
            fontWeight="bold"
          >
            {formatLevel(level)} m
          </text>
          {/* Leader line from tag to tank */}
          <line
            x1={tankRight + 30}
            y1={tankTop + 38}
            x2={tankRight + 4}
            y2={tankTop + 38}
            stroke={tagBorder}
            strokeWidth={0.5}
            strokeDasharray="2,2"
          />
        </g>

        {/* FI-101: Outlet flow tag (near outlet pipe, below valve) */}
        <g>
          <rect
            x={650}
            y={valveY - 40}
            width={100}
            height={36}
            rx={3}
            fill={tagBg}
            stroke={tagBorder}
            strokeWidth={1}
          />
          <text
            x={700}
            y={valveY - 26}
            fontSize={tagFontSize}
            fill={tagText}
            textAnchor="middle"
            fontFamily="monospace"
          >
            FI-101
          </text>
          <text
            x={700}
            y={valveY - 11}
            fontSize={tagValueFontSize}
            fill={tagValue}
            textAnchor="middle"
            fontFamily="monospace"
            fontWeight="bold"
          >
            {formatFlowRate(outletFlow)} m³/s
          </text>
        </g>

        {/* VP-100: Valve position tag (beneath valve) */}
        <g>
          <rect
            x={valveX - 45}
            y={valveY + valveSize + 4}
            width={90}
            height={36}
            rx={3}
            fill={tagBg}
            stroke={tagBorder}
            strokeWidth={1}
          />
          <text
            x={valveX}
            y={valveY + valveSize + 18}
            fontSize={tagFontSize}
            fill={tagText}
            textAnchor="middle"
            fontFamily="monospace"
          >
            VP-100
          </text>
          <text
            x={valveX}
            y={valveY + valveSize + 33}
            fontSize={tagValueFontSize}
            fill={tagValue}
            textAnchor="middle"
            fontFamily="monospace"
            fontWeight="bold"
          >
            {formatValvePosition(valvePosition)}
          </text>
        </g>

        {/* === CONTROL LOOP FACEPLATE (LIC-100) === */}
        <g>
          <rect
            x={tankRight + 30}
            y={tankTop + 80}
            width={170}
            height={120}
            rx={3}
            fill={tagBg}
            stroke="#6b7280"
            strokeWidth={1.5}
          />
          {/* Title bar */}
          <rect
            x={tankRight + 30}
            y={tankTop + 80}
            width={170}
            height={20}
            rx={3}
            fill="#374151"
          />
          <text
            x={tankRight + 115}
            y={tankTop + 94}
            fontSize={11}
            fill="#e5e7eb"
            textAnchor="middle"
            fontFamily="monospace"
            fontWeight="bold"
          >
            LIC-100
          </text>

          {/* PV row */}
          <text
            x={tankRight + 38}
            y={tankTop + 115}
            fontSize={10}
            fill="#9ca3af"
            fontFamily="monospace"
          >
            PV
          </text>
          <text
            x={tankRight + 140}
            y={tankTop + 115}
            fontSize={11}
            fill="#e5e7eb"
            textAnchor="end"
            fontFamily="monospace"
          >
            {formatLevel(level)} m
          </text>

          {/* SP row */}
          <text
            x={tankRight + 38}
            y={tankTop + 133}
            fontSize={10}
            fill="#9ca3af"
            fontFamily="monospace"
          >
            SP
          </text>
          {/* SP editable input via foreignObject */}
          <foreignObject
            x={tankRight + 80}
            y={tankTop + 121}
            width={65}
            height={20}
          >
            <input
              type="text"
              value={localSetpoint}
              onChange={(e) => {
                setLocalSetpoint(e.target.value);
                setIsEditingSetpoint(true);
              }}
              onBlur={handleSetpointSubmit}
              onKeyDown={handleSetpointKeyDown}
              onFocus={() => setIsEditingSetpoint(true)}
              style={{
                width: "100%",
                height: "100%",
                background: "#374151",
                color: "#e5e7eb",
                border: "1px solid #6b7280",
                borderRadius: "2px",
                padding: "0 4px",
                fontSize: "11px",
                fontFamily: "monospace",
                textAlign: "right",
                outline: "none",
              }}
            />
          </foreignObject>
          <text
            x={tankRight + 150}
            y={tankTop + 133}
            fontSize={10}
            fill="#9ca3af"
            fontFamily="monospace"
          >
            m
          </text>

          {/* OP row */}
          <text
            x={tankRight + 38}
            y={tankTop + 151}
            fontSize={10}
            fill="#9ca3af"
            fontFamily="monospace"
          >
            OP
          </text>
          <text
            x={tankRight + 140}
            y={tankTop + 151}
            fontSize={11}
            fill="#e5e7eb"
            textAnchor="end"
            fontFamily="monospace"
          >
            {formatValvePosition(controllerOutput)}
          </text>

          {/* Error row */}
          <text
            x={tankRight + 38}
            y={tankTop + 169}
            fontSize={10}
            fill="#9ca3af"
            fontFamily="monospace"
          >
            Err
          </text>
          <text
            x={tankRight + 140}
            y={tankTop + 169}
            fontSize={11}
            fill={
              Math.abs(error) < 0.2
                ? "#9ca3af"
                : Math.abs(error) < 0.5
                  ? "#eab308"
                  : "#ef4444"
            }
            textAnchor="end"
            fontFamily="monospace"
          >
            {error >= 0 ? "+" : ""}
            {error.toFixed(2)} m
          </text>

          {/* PID tuning button (wrench icon) */}
          <g onClick={onPIDPopoverToggle} style={{ cursor: "pointer" }}>
            <rect
              x={tankRight + 155}
              y={tankTop + 82}
              width={16}
              height={16}
              rx={2}
              fill="#374151"
              stroke="#6b7280"
              strokeWidth={0.5}
            />
            {/* Simple wrench/gear icon using Unicode */}
            <text
              x={tankRight + 163}
              y={tankTop + 94}
              fontSize={11}
              fill="#9ca3af"
              textAnchor="middle"
              style={{ cursor: "pointer" }}
            >
              &#x2699;
            </text>
          </g>

          {/* Leader line from faceplate to tank */}
          <line
            x1={tankRight + 30}
            y1={tankTop + 140}
            x2={tankRight + 4}
            y2={tankTop + 140}
            stroke="#6b7280"
            strokeWidth={0.5}
            strokeDasharray="2,2"
          />
        </g>

        {/* === CONTROL SIGNAL LINE (LIC-100 to CV-100) === */}
        <line
          x1={valveX}
          y1={tankTop + 200}
          x2={valveX}
          y2={valveY - valveSize - 22}
          stroke="#6b7280"
          strokeWidth={1}
          strokeDasharray="4,3"
        />
        {/* Horizontal segment from faceplate to vertical line */}
        <line
          x1={tankRight + 115}
          y1={tankTop + 200}
          x2={valveX}
          y2={tankTop + 200}
          stroke="#6b7280"
          strokeWidth={1}
          strokeDasharray="4,3"
        />

        {/* === LABELS === */}

        {/* Tank label */}
        <text
          x={tankLeft + tankWidth / 2}
          y={tankTop - 8}
          fontSize={12}
          fill="#9ca3af"
          textAnchor="middle"
          fontFamily="monospace"
        >
          TK-100
        </text>

        {/* Valve label */}
        <text
          x={valveX}
          y={valveY - valveSize - 26}
          fontSize={10}
          fill="#9ca3af"
          textAnchor="middle"
          fontFamily="monospace"
        >
          CV-100
        </text>

        {/* Flow direction arrows (static, non-animated) */}
        {/* Inlet arrow */}
        <polygon
          points={`60,${tankTop + 26} 70,${tankTop + 30} 60,${tankTop + 34}`}
          fill={inletFlow > 0 ? "#6b7280" : "#4b5563"}
        />
        {/* Outlet arrow */}
        <polygon
          points={`730,${valveY - 4} 740,${valveY} 730,${valveY + 4}`}
          fill={outletFlow > 0 ? "#6b7280" : "#4b5563"}
        />
      </svg>
    </div>
  );
}
