import React from "react";
import { countToday } from "../utils";

function SectionTitle({ children }) {
  return (
    <div className="flex items-center gap-2 text-[#dbe3ee] text-[11px] font-bold tracking-wider mt-3.5 mb-2">
      {children}
      <span className="flex-1 h-px bg-[#161f2c]" />
    </div>
  );
}

function Card({ label, value, delta, accent }) {
  return (
    <div
      className="bg-gradient-to-br from-[#0d131e] to-[#080d15] border border-[#1c2736] rounded-[9px] px-[13px] py-[11px] min-h-[78px]"
      style={{ borderLeft: `3px solid ${accent}` }}
    >
      <div className="text-[#8490a2] text-[9px] font-bold tracking-wide">{label}</div>
      <div className="text-white text-[25px] font-extrabold mt-[3px] leading-tight">
        {value.toLocaleString()}
      </div>
      {delta > 0 ? (
        <div className="text-[#35cf66] text-[9.5px] font-bold mt-1">↑ {delta} today</div>
      ) : (
        <div className="text-[#6d7c93] text-[9.5px] font-bold mt-1">No change today</div>
      )}
    </div>
  );
}

export default function KpiCards({ filtered, allFires }) {
  const totalEvents = filtered.length;
  const totalEventsToday = countToday(filtered);

  // Backend-assigned risk_level of HIGH/CRITICAL — never re-derived from
  // a local score cutoff, matching app.py's FIX comment.
  const highRisk = filtered.filter((r) => ["HIGH", "CRITICAL"].includes(r.risk_level));
  const persistent = filtered.filter((r) => r.classification === "THERMAL_SOURCE");
  const industrial = filtered.filter((r) => r.classification === "INDUSTRIAL_FIRE");

  const defs = [
    ["🔥 ACTIVE EVENTS", totalEvents, totalEventsToday, "#ef4444"],
    ["🛡 HIGH RISK", highRisk.length, countToday(highRisk), "#ff8a00"],
    ["⟳ PERSISTENT SOURCES", persistent.length, countToday(persistent), "#a855f7"],
    ["🏭 INDUSTRIAL PROXIMITY", industrial.length, countToday(industrial), "#35cf66"],
    ["◎ TOTAL DETECTIONS", allFires.length, countToday(allFires), "#24aef5"],
  ];

  return (
    <>
      <SectionTitle>LIVE MONITORING</SectionTitle>
      <div className="grid grid-cols-5 gap-3">
        {defs.map(([label, value, delta, accent]) => (
          <Card key={label} label={label} value={value} delta={delta} accent={accent} />
        ))}
      </div>
    </>
  );
}

export { SectionTitle };
