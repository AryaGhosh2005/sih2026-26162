import React, { useMemo } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { CLASS_COLORS } from "../constants";
import { SectionTitle } from "./KpiCards";
import { toDateOnly } from "../utils";

function Panel({ title, children }) {
  return (
    <div className="bg-[#0a1019] border border-[#1b2635] rounded-[10px] p-3">
      <div className="text-[#cdd6e3] text-[10.5px] font-bold tracking-wide mb-0.5">{title}</div>
      {children}
    </div>
  );
}

const tooltipStyle = {
  background: "#0d1420",
  border: "1px solid #283446",
  borderRadius: 8,
  fontSize: 11,
  color: "#e8edf5",
};

export default function AnalyticsCharts({ filtered }) {
  const daily = useMemo(() => {
    const byDate = {};
    for (const r of filtered) {
      const d = toDateOnly(r.acquisition_date);
      if (!d) continue;
      byDate[d] ??= { date: d, count: 0, riskSum: 0, riskCount: 0 };
      byDate[d].count += 1;
      byDate[d].riskSum += Number(r.risk_score) || 0;
      byDate[d].riskCount += 1;
    }
    return Object.values(byDate)
      .sort((a, b) => a.date.localeCompare(b.date))
      .map((d) => ({ date: d.date.slice(5), count: d.count, risk_score: d.riskSum / d.riskCount }));
  }, [filtered]);

  const distribution = useMemo(() => {
    const counts = {};
    for (const r of filtered) {
      const label = r.classification_label || "Unknown";
      counts[label] = (counts[label] || 0) + 1;
    }
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [filtered]);

  return (
    <div>
      <SectionTitle>FIRE DETECTION ANALYTICS</SectionTitle>
      <div className="grid grid-cols-3 gap-3">
        <Panel title="THERMAL ACTIVITY — LAST 7 DAYS">
          {daily.length ? (
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={daily} margin={{ top: 6, right: 10, left: 10, bottom: 10 }}>
                <CartesianGrid stroke="#141d2a" />
                <XAxis dataKey="date" tick={{ fill: "#aeb8c7", fontSize: 10 }} />
                <YAxis tick={{ fill: "#aeb8c7", fontSize: 10 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="count" stroke="#ef4444" fill="rgba(239,68,68,0.15)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-[#9aa6ba] text-xs py-10 text-center">No data available.</div>
          )}
        </Panel>

        <Panel title="RISK TREND — LAST 7 DAYS">
          {daily.length ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={daily} margin={{ top: 6, right: 10, left: 10, bottom: 10 }}>
                <CartesianGrid stroke="#141d2a" />
                <XAxis dataKey="date" tick={{ fill: "#aeb8c7", fontSize: 10 }} />
                <YAxis tick={{ fill: "#aeb8c7", fontSize: 10 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Line type="monotone" dataKey="risk_score" stroke="#ff8a00" dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-[#9aa6ba] text-xs py-10 text-center">No data available.</div>
          )}
        </Panel>

        <Panel title="SOURCE DISTRIBUTION">
          {distribution.length ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={distribution} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90}>
                  {distribution.map((d) => (
                    <Cell key={d.name} fill={CLASS_COLORS[d.name] || "#64748b"} stroke="#0a1019" strokeWidth={2} />
                  ))}
                </Pie>
                <Legend wrapperStyle={{ fontSize: 9 }} />
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-[#9aa6ba] text-xs py-10 text-center">No data available.</div>
          )}
        </Panel>
      </div>
    </div>
  );
}
