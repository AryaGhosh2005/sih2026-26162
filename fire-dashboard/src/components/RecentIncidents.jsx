import React, { useMemo } from "react";
import { CLASS_NAMES, RISK_ICONS, riskColor } from "../constants";
import { SectionTitle } from "./KpiCards";

export default function RecentIncidents({ filtered }) {
  const feed = useMemo(
    () => [...filtered].sort((a, b) => (Number(b.risk_score) || 0) - (Number(a.risk_score) || 0)).slice(0, 4),
    [filtered]
  );

  return (
    <div>
      <SectionTitle>RECENT INCIDENTS</SectionTitle>

      {!feed.length ? (
        <div className="bg-[#0c1622] border border-[#24354a] rounded-md text-[#9aa6ba] text-xs px-3 py-2.5">
          No intelligence events available.
        </div>
      ) : (
        <div className="grid grid-cols-4 gap-3">
          {feed.map((event, i) => {
            const score = Math.round(Number(event.risk_score) || 0);
            const risk = event.risk_level || "LOW";
            const classification = CLASS_NAMES[event.classification] || "Unknown";
            const hex = riskColor(risk);
            const icon = RISK_ICONS[risk] || "⚪";
            const time = event.acquisition_date
              ? new Date(event.acquisition_date).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })
              : "N/A";

            return (
              <div
                key={event.id ?? i}
                className="bg-[#0a1019] border border-[#1b2635] rounded-[9px] p-3 min-h-[130px]"
                style={{ borderLeft: `3px solid ${hex}` }}
              >
                <div className="text-[#6f7d91] text-[9px]">{time}</div>
                <div className="text-[10px] font-extrabold mt-1 tracking-wide" style={{ color: hex }}>
                  {icon} {risk}
                </div>
                <div className="text-[#e6ebf2] text-[11.5px] font-semibold mt-1.5">
                  {classification} detected
                </div>
                <div className="text-[#778499] text-[9px] mt-2 leading-relaxed">
                  Confidence: {event.confidence ?? "N/A"}%
                  <br />
                  Distance: {event.distance_to_industry ?? "N/A"} km
                  <br />
                  Risk Score: {score}/100
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
