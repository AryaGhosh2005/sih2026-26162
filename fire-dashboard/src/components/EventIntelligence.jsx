import React from "react";
import { CLASS_NAMES, riskColor } from "../constants";
import { explainEvent } from "../utils";
import { SectionTitle } from "./KpiCards";

function Row({ label, value, color }) {
  return (
    <div className="flex justify-between gap-2.5 border-b border-[#18202c] last:border-b-0 py-[7px] text-[10.5px]">
      <span className="text-[#788599]">{label}</span>
      <span className="font-semibold text-right" style={{ color: color || "#e5ebf3" }}>
        {value}
      </span>
    </div>
  );
}

export default function EventIntelligence({ event }) {
  return (
    <div>
      <SectionTitle>EVENT INTELLIGENCE</SectionTitle>

      {!event ? (
        <div className="bg-[#0c1622] border border-[#24354a] rounded-md text-[#9aa6ba] text-xs px-3 py-2.5">
          No events match the selected filters.
        </div>
      ) : (
        <>
          {(() => {
            const classification = event.classification || "UNKNOWN";
            const eventType = CLASS_NAMES[classification] || "Unknown";
            const score = Math.round(Number(event.risk_score) || 0);
            const risk = event.risk_level || "LOW";
            const hex = riskColor(risk);
            const eventId = event.id ?? `IND-${String(event._index ?? 0).padStart(4, "0")}`;

            return (
              <div className="bg-[#0a1019] border border-[#1b2635] rounded-[9px] p-[13px] mb-2" style={{ borderLeft: `3px solid ${hex}` }}>
                <div className="text-white text-[17px] font-extrabold">{eventId}</div>
                <div className="text-[10px] font-extrabold tracking-wide mt-0.5" style={{ color: hex }}>
                  {eventType.toUpperCase()}
                </div>

                <Row label="Risk Level" value={risk} color={hex} />
                <Row label="Risk Score" value={`${score}/100`} />
                <Row label="Confidence" value={`${event.confidence ?? "N/A"}%`} />
                <Row label="Brightness" value={`${event.brightness ?? "N/A"} K`} />
                <Row label="Distance" value={`${event.distance_to_industry ?? "N/A"} km`} />
                <Row label="Satellite" value={event.satellite ?? "N/A"} />
              </div>
            );
          })()}

          <SectionTitle>AI EXPLANATION</SectionTitle>
          <div className="bg-[#0a1019] border border-[#1b2635] rounded-[9px] p-[13px]">
            {explainEvent(event).map((row) => (
              <div key={row.label} className="mb-[9px]">
                <div className="text-[9.5px] text-[#b8c3d2] mb-1 flex justify-between">
                  <span>{row.label}</span>
                  <span className="text-[#35cf66]">{row.value}%</span>
                </div>
                <div className="h-1 bg-[#182433] rounded-[5px]">
                  <div
                    className="h-1 bg-[#35cf66] rounded-[5px]"
                    style={{ width: `${row.value}%` }}
                  />
                </div>
              </div>
            ))}
            <div className="mt-2 bg-[#0d1723] border border-[#203044] rounded-md text-[#9ba8ba] text-[9.5px] leading-relaxed px-2.5 py-2">
              High probability of industrial thermal activity based on industrial proximity,
              thermal intensity, persistence and detection confidence.
            </div>
          </div>
        </>
      )}
    </div>
  );
}
