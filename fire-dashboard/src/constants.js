// Ported 1:1 from app.py's CONSTANTS block.

export const CLASS_NAMES = {
  INDUSTRIAL_FIRE: "Industrial Fire",
  WILDFIRE: "Wildfire",
  THERMAL_SOURCE: "Thermal Source",
  UNKNOWN: "Unknown",
};

// Marker/legend colors, ported from map_visualization.py's CLASS_COLORS
// (kept separate from the KPI/chart palette below, matching the source).
export const MAP_CLASS_COLORS = {
  INDUSTRIAL_FIRE: "#FF0000",
  WILDFIRE: "#FF8C00",
  THERMAL_SOURCE: "#00CC00",
  UNKNOWN: "#0066CC",
};

// Chart / pie palette, ported from app.py's CLASS_COLORS (keyed by label).
export const CLASS_COLORS = {
  "Industrial Fire": "#ef4444",
  Wildfire: "#ff8a00",
  "Persistent Source": "#a855f7",
  "Thermal Source": "#a855f7",
  Unknown: "#64748b",
};

// Matches risk_engine.get_risk_level() exactly — CRITICAL/HIGH/MODERATE/LOW.
export const RISK_COLORS = {
  CRITICAL: "#ef4444",
  HIGH: "#ff8a00",
  MODERATE: "#f5bd24",
  LOW: "#35cf66",
};

export const RISK_ICONS = {
  CRITICAL: "🔴",
  HIGH: "🟠",
  MODERATE: "🟡",
  LOW: "🟢",
};

export const RISK_OPTIONS = [
  { key: "CRITICAL", label: "🔴 Critical" },
  { key: "HIGH", label: "🟠 High" },
  { key: "MODERATE", label: "🟡 Moderate" },
  { key: "LOW", label: "🟢 Low" },
];

export const SOURCE_TYPES = [
  "Industrial Fire",
  "Thermal Source",
  "Wildfire",
  "Unknown",
];

export function riskColor(risk) {
  return RISK_COLORS[risk] || "#64748b";
}
