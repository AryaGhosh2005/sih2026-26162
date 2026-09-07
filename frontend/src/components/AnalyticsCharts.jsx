//AnalyticsCharts.jsx
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

/* ============================================================
   PANEL
============================================================ */

function Panel({ title, children }) {
  return (
    <div className="bg-[#0a1019] border border-[#1b2635] rounded-[10px] p-3">
      <div className="text-[#cdd6e3] text-[10.5px] font-bold tracking-wide mb-0.5">
        {title}
      </div>

      {children}
    </div>
  );
}

/* ============================================================
   TOOLTIP
============================================================ */

const tooltipStyle = {
  background: "#0d1420",
  border: "1px solid #283446",
  borderRadius: 8,
  fontSize: 11,
  color: "#ffffff",
};

/* ============================================================
   CSV EXPORT
============================================================ */

function handleExportCSV(filtered) {
  if (!filtered || filtered.length === 0) {
    alert("No fire detection data available to export.");
    return;
  }

  // Get every field present in the dataset
  const headers = [
    ...new Set(
      filtered.flatMap((item) => Object.keys(item))
    ),
  ];

  const escapeValue = (value) => {
    if (value === null || value === undefined) {
      return "";
    }

    const text = String(value);

    if (
      text.includes(",") ||
      text.includes('"') ||
      text.includes("\n")
    ) {
      return `"${text.replace(/"/g, '""')}"`;
    }

    return text;
  };

  const rows = [];

  // Header
  rows.push(
    headers.map(escapeValue).join(",")
  );

  // Data
  filtered.forEach((item) => {
    rows.push(
      headers
        .map((header) => escapeValue(item[header]))
        .join(",")
    );
  });

  const csv = rows.join("\n");

  const blob = new Blob([csv], {
    type: "text/csv;charset=utf-8;",
  });

  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");

  link.href = url;
  link.download = `fire-detections-${new Date()
    .toISOString()
    .slice(0, 10)}.csv`;

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}

/* ============================================================
   GEOJSON EXPORT
============================================================ */

function handleExportGeoJSON(filtered) {
  if (!filtered || filtered.length === 0) {
    alert("No fire detection data available to export.");
    return;
  }

  const features = [];

  filtered.forEach((fire) => {
    /*
      Your data may use different coordinate field names.
      We check the common possibilities.
    */

    const latitude = Number(
      fire.latitude ??
        fire.lat ??
        fire.lat_dd ??
        fire.y
    );

    const longitude = Number(
      fire.longitude ??
        fire.lon ??
        fire.lng ??
        fire.long ??
        fire.lon_dd ??
        fire.x
    );

    if (
      Number.isNaN(latitude) ||
      Number.isNaN(longitude)
    ) {
      return;
    }

    const properties = {
      ...fire,
    };

    // Don't duplicate coordinates inside properties
    delete properties.latitude;
    delete properties.longitude;
    delete properties.lat;
    delete properties.lon;
    delete properties.lng;
    delete properties.long;
    delete properties.lat_dd;
    delete properties.lon_dd;

    features.push({
      type: "Feature",

      geometry: {
        type: "Point",
        coordinates: [
          longitude,
          latitude,
        ],
      },

      properties,
    });
  });

  if (features.length === 0) {
    alert(
      "No valid latitude and longitude values were found in the fire data."
    );
    return;
  }

  const geojson = {
    type: "FeatureCollection",
    features,
  };

  const blob = new Blob(
    [
      JSON.stringify(
        geojson,
        null,
        2
      ),
    ],
    {
      type: "application/geo+json;charset=utf-8;",
    }
  );

  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");

  link.href = url;
  link.download = `fire-detections-${new Date()
    .toISOString()
    .slice(0, 10)}.geojson`;

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}

/* ============================================================
   EXPORT BUTTON
============================================================ */

function ExportButton({
  title,
  description,
  icon,
  accent,
  onClick,
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="
        group
        relative
        flex-1
        overflow-hidden
        rounded-xl
        border
        px-4
        py-2.5
        text-left
        transition-all
        duration-200
        hover:-translate-y-[1px]
        active:translate-y-0
      "
      style={{
        borderColor: `${accent}55`,

        background:
          "linear-gradient(135deg, rgba(7,16,27,0.98), rgba(10,20,32,0.90))",

        boxShadow: `
          0 0 10px ${accent}12,
          inset 0 1px 0 rgba(255,255,255,0.06)
        `,
      }}
    >

      {/* TOP ACCENT */}
      <div
        className="absolute left-5 right-5 top-0 h-px"
        style={{
          background: accent,
          boxShadow: `0 0 8px ${accent}`,
        }}
      />

      {/* HOVER GLOW */}
      <div
        className="
          pointer-events-none
          absolute
          -right-8
          -top-8
          h-20
          w-20
          rounded-full
          blur-2xl
          opacity-0
          transition-opacity
          duration-300
          group-hover:opacity-20
        "
        style={{
          background: accent,
        }}
      />

      <div className="relative flex items-center gap-3">

        {/* ICON */}
        <div
          className="
            flex
            h-8
            w-8
            shrink-0
            items-center
            justify-center
            rounded-lg
            border
            bg-white/[0.025]
          "
          style={{
            borderColor: `${accent}55`,
            color: accent,
          }}
        >
          <span
            className="text-[15px] font-bold"
            style={{
              filter: `drop-shadow(0 0 4px ${accent})`,
            }}
          >
            {icon}
          </span>
        </div>

        {/* TEXT */}
        <div className="min-w-0">

          <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-white">
            {title}
          </div>

          <div className="mt-0.5 text-[8px] text-slate-500">
            {description}
          </div>

        </div>

        {/* ARROW */}
        <div
          className="
            ml-auto
            text-[13px]
            opacity-40
            transition-all
            duration-200
            group-hover:translate-x-1
            group-hover:opacity-90
          "
          style={{
            color: accent,
          }}
        >
          →
        </div>

      </div>

      {/* BOTTOM ACCENT */}
      <div
        className="absolute bottom-0 left-5 right-5 h-px opacity-40"
        style={{
          background: accent,
        }}
      />

    </button>
  );
}

/* ============================================================
   MAIN ANALYTICS
============================================================ */

export default function AnalyticsCharts({
  filtered,
}) {

  /* ==========================================================
     DAILY DATA
  ========================================================== */

  const daily = useMemo(() => {

    const byDate = {};

    for (const r of filtered) {

      const d = toDateOnly(
        r.acquisition_date
      );

      if (!d) continue;

      byDate[d] ??= {
        date: d,
        count: 0,
        riskSum: 0,
        riskCount: 0,
      };

      byDate[d].count += 1;

      byDate[d].riskSum +=
        Number(r.risk_score) || 0;

      byDate[d].riskCount += 1;
    }

    return Object.values(byDate)
      .sort((a, b) =>
        a.date.localeCompare(b.date)
      )
      .map((d) => ({
        date: d.date.slice(5),

        count: d.count,

        risk_score:
          d.riskCount > 0
            ? d.riskSum /
              d.riskCount
            : 0,
      }));

  }, [filtered]);

  /* ==========================================================
     SOURCE DISTRIBUTION
  ========================================================== */

  const distribution = useMemo(() => {

    const counts = {};

    for (const r of filtered) {

      const label =
        r.classification_label ||
        "Unknown";

      counts[label] =
        (counts[label] || 0) + 1;
    }

    return Object.entries(
      counts
    ).map(([name, value]) => ({
      name,
      value,
    }));

  }, [filtered]);

  /* ==========================================================
     UI
  ========================================================== */

  return (
    <div>

      {/* SECTION TITLE */}

      <SectionTitle>
        FIRE DETECTION ANALYTICS
      </SectionTitle>


      {/* ======================================================
          THREE CHARTS
      ====================================================== */}

      <div className="grid grid-cols-3 gap-3">

        {/* ====================================================
            THERMAL ACTIVITY
        ==================================================== */}

        <Panel title="THERMAL ACTIVITY — LAST 7 DAYS">

          {daily.length ? (

            <ResponsiveContainer
              width="100%"
              height={250}
            >

              <AreaChart
                data={daily}
                margin={{
                  top: 6,
                  right: 10,
                  left: 10,
                  bottom: 10,
                }}
              >

                <CartesianGrid
                  stroke="#141d2a"
                />

                <XAxis
                  dataKey="date"
                  tick={{
                    fill: "#aeb8c7",
                    fontSize: 10,
                  }}
                />

                <YAxis
                  tick={{
                    fill: "#aeb8c7",
                    fontSize: 10,
                  }}
                />

                <Tooltip
                  contentStyle={
                    tooltipStyle
                  }
                />

                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#ef4444"
                  fill="rgba(239,68,68,0.15)"
                />

              </AreaChart>

            </ResponsiveContainer>

          ) : (

            <div className="py-10 text-center text-xs text-[#9aa6ba]">
              No data available.
            </div>

          )}

        </Panel>


        {/* ====================================================
            RISK TREND
        ==================================================== */}

        <Panel title="RISK TREND — LAST 7 DAYS">

          {daily.length ? (

            <ResponsiveContainer
              width="100%"
              height={250}
            >

              <LineChart
                data={daily}
                margin={{
                  top: 6,
                  right: 10,
                  left: 10,
                  bottom: 10,
                }}
              >

                <CartesianGrid
                  stroke="#141d2a"
                />

                <XAxis
                  dataKey="date"
                  tick={{
                    fill: "#aeb8c7",
                    fontSize: 10,
                  }}
                />

                <YAxis
                  tick={{
                    fill: "#aeb8c7",
                    fontSize: 10,
                  }}
                />

                <Tooltip
                  contentStyle={
                    tooltipStyle
                  }
                />

                <Line
                  type="monotone"
                  dataKey="risk_score"
                  stroke="#ff8a00"
                  dot={{
                    r: 3,
                  }}
                />

              </LineChart>

            </ResponsiveContainer>

          ) : (

            <div className="py-10 text-center text-xs text-[#9aa6ba]">
              No data available.
            </div>

          )}

        </Panel>


        {/* ====================================================
            SOURCE DISTRIBUTION
        ==================================================== */}

        <Panel title="SOURCE DISTRIBUTION">

          {distribution.length ? (

            <ResponsiveContainer
              width="100%"
              height={250}
            >

              <PieChart>

                <Pie
                  data={distribution}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={55}
                  outerRadius={90}
                >

                  {distribution.map(
                    (d) => (

                      <Cell
                        key={d.name}
                        fill={
                          CLASS_COLORS[
                            d.name
                          ] ||
                          "#64748b"
                        }
                        stroke="#0a1019"
                        strokeWidth={2}
                      />

                    )
                  )}

                </Pie>

                <Legend
                  wrapperStyle={{
                    fontSize: 9,
                  }}
                />

                <Tooltip
                  contentStyle={
                    tooltipStyle
                  }
                />

              </PieChart>

            </ResponsiveContainer>

          ) : (

            <div className="py-10 text-center text-xs text-[#9aa6ba]">
              No data available.
            </div>

          )}

        </Panel>

      </div>


      {/* ======================================================
          EXPORT BUTTONS
          THESE ARE DIRECTLY UNDER THE THREE CHARTS
      ====================================================== */}

      <div className="mt-3 flex w-full gap-3">

        <ExportButton
          title="Export CSV"
          description={`${filtered.length} detections • Download tabular data`}
          icon="↓"
          accent="#00cfff"
          onClick={() =>
            handleExportCSV(filtered)
          }
        />

        <ExportButton
          title="Export GeoJSON"
          description={`${filtered.length} detections • Download map data`}
          icon="◇"
          accent="#00e69a"
          onClick={() =>
            handleExportGeoJSON(filtered)
          }
        />

      </div>

    </div>
  );
}