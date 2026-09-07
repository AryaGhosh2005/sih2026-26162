//App.jsx
import React, { useEffect, useMemo, useState, useCallback } from "react";
import {
  ChevronRight,
  ChevronLeft,
  ChevronUp,
  ChevronDown,
} from "lucide-react";

import Sidebar from "./components/Sidebar";
import KpiCards from "./components/KpiCards";
import FireMap from "./components/FireMap";
import EventIntelligence from "./components/EventIntelligence";
import AnalyticsCharts from "./components/AnalyticsCharts";

import { loadData } from "./api";
import { applyFilters, toDateOnly } from "./utils";
import { RISK_OPTIONS, SOURCE_TYPES } from "./constants";

function defaultFilters(fires) {
  const dates = fires
    .map((f) => toDateOnly(f.acquisition_date))
    .filter(Boolean);

  const startDate = dates.length
    ? dates.reduce((a, b) => (a < b ? a : b))
    : toDateOnly(new Date());

  const endDate = dates.length
    ? dates.reduce((a, b) => (a > b ? a : b))
    : toDateOnly(new Date());

  const distances = fires
    .map((f) => Number(f.distance_to_industry))
    .filter((n) => !Number.isNaN(n));

  const dataMaxDistance = distances.length
    ? Math.floor(Math.max(...distances)) + 1
    : 2000;

  const satellites = [
    ...new Set(fires.map((f) => String(f.satellite))),
  ].sort();

  return {
    startDate,
    endDate,
    selectedRiskKeys: RISK_OPTIONS.map((o) => o.key),
    selectedSources: [...SOURCE_TYPES],
    selectedSatellites: satellites,
    minConfidence: 0,
    minBrightness: 280,
    maxDistance: dataMaxDistance,
    dataMaxDistance,
  };
}

export default function App() {
  const [fires, setFires] = useState([]);
  const [industries, setIndustries] = useState([]);
  const [filters, setFilters] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [now, setNow] = useState(new Date());

  /* =========================================================
     COLLAPSIBLE PANEL STATES
     ========================================================= */

  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [bottomCollapsed, setBottomCollapsed] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const { fires: f, industries: ind } = await loadData();

      setFires(f);
      setIndustries(ind);
      setFilters((prev) => prev ?? defaultFilters(f));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();

    const id = setInterval(fetchData, 5 * 60 * 1000);

    return () => clearInterval(id);
  }, [fetchData, refreshKey]);

  useEffect(() => {
  const timer = setInterval(() => {
    setNow(new Date());
  }, 1000);

  return () => clearInterval(timer);
  }, []);

  const satellites = useMemo(
    () => [...new Set(fires.map((f) => String(f.satellite)))].sort(),
    [fires]
  );

  const filtered = useMemo(() => {
    if (!filters) return [];

    return applyFilters(fires, filters);
  }, [fires, filters]);

  useEffect(() => {
    if (filtered.length) {
  const highestRisk = [...filtered].sort(
    (a, b) => b.risk_score - a.risk_score
  )[0];

  setSelectedEvent(highestRisk);
} else if (!filtered.length) {
      setSelectedEvent(null);
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtered]);

  /* =========================================================
     LOADING STATE
     ========================================================= */

  if (loading && !filters) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#02060b] text-[#8490a2] text-sm">
        Loading fire detection data…
      </div>
    );
  }

  /* =========================================================
     ERROR STATE
     ========================================================= */

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#02060b] p-6">
        <div className="bg-[#0c1622] border border-[#24354a] rounded-md text-[#f5a3a3] text-sm px-4 py-3 max-w-lg">
          {error}
        </div>
      </div>
    );
  }

  /* =========================================================
     MAIN COMMAND CENTER
     ========================================================= */

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-[#02060b] text-white">

      {/* =========================================================
          FULLSCREEN MAP CANVAS
         ========================================================= */}

      <div className="absolute inset-0 z-0">
        <FireMap
          fires={filtered}
          industries={industries}
          onSelectEvent={setSelectedEvent}
        />
      </div>


      {/* =========================================================
          FLOATING COMMAND CENTER UI
         ========================================================= */}

      <div className="pointer-events-none absolute inset-0 z-10">


        {/* =======================================================
            BRAND PANEL
           ======================================================= */}

        <div className="pointer-events-auto absolute left-4 top-4 z-30">

          <div className="rounded-2xl border border-cyan-400/25 bg-[#07101b]/80 px-5 py-3 backdrop-blur-2xl shadow-[0_0_30px_rgba(0,180,255,0.10)]">

            <div className="flex items-center gap-3">

              <div className="text-3xl">
                🔥
              </div>

              <div>

                <div className="text-xl font-black tracking-wide text-white">
                  INDUSTRIAL FIRE
                </div>

                <div className="text-[11px] font-medium tracking-[0.2em] text-cyan-300 leading-tight">
  INDUSFIRE AI
  <br />
  <span className="text-[9px] text-slate-400 tracking-[0.15em]">
    AI THERMAL INTELLIGENCE PLATFORM
  </span>
</div>

                <div className="mt-1 text-[9px] text-slate-400">
                  Satellite Intelligence&nbsp; | &nbsp;Industrial Safety&nbsp; | &nbsp;A Safer Tomorrow
                </div>

              </div>

            </div>

          </div>

        </div>


        {/* =======================================================
            KPI CARDS
           ======================================================= */}

        <div className="pointer-events-auto absolute left-1/2 top-4 z-30 w-[min(850px,55vw)] -translate-x-1/2">

          <KpiCards
            filtered={filtered}
            allFires={fires}
          />

        </div>


        {/* =======================================================
            SYSTEM STATUS + CLOCK
           ======================================================= */}

        <div className="pointer-events-auto absolute right-[175px] top-4 z-30 flex items-center gap-2">

          {/* SYSTEM STATUS */}

          <div className="rounded-xl border border-cyan-400/20 bg-[#07101b]/85 px-5 py-3 text-center backdrop-blur-2xl shadow-[0_0_25px_rgba(0,180,255,0.08)]">

            <div className="text-[8px] uppercase tracking-widest text-slate-500">
              System Status
            </div>

            <div className="mt-1 flex items-center justify-center gap-2 text-[11px] font-bold text-emerald-400">

              <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.9)]" />

              MONITORING ACTIVE

            </div>

          </div>


          {/* CLOCK */}

          <div className="rounded-xl border border-cyan-400/20 bg-[#07101b]/85 px-5 py-3 text-center backdrop-blur-2xl shadow-[0_0_25px_rgba(0,180,255,0.08)]">

            <div className="text-sm font-bold text-white whitespace-nowrap">
              {now.toLocaleTimeString()}
            </div>

            <div className="text-[8px] text-slate-500 whitespace-nowrap">
              {now.toLocaleTimeString()}
            </div>

          </div>

        </div>


        {/* =======================================================
            LEFT CONTROL PANEL
            COLLAPSIBLE
           ======================================================= */}

        {!leftCollapsed ? (

          <div className="pointer-events-auto absolute bottom-24 left-4 top-28 z-30 w-[220px]">

            <div className="relative h-full overflow-hidden rounded-2xl border border-cyan-400/20 bg-[#050b13]/75 backdrop-blur-2xl shadow-[0_0_35px_rgba(0,200,255,0.08)]">

              <Sidebar
                filters={filters}
                setFilters={setFilters}
                dataStatus={{ total: fires.length }}
                onRefresh={() => setRefreshKey((k) => k + 1)}
                satellites={satellites}
              />

              {/* COLLAPSE BUTTON */}

              <button
                onClick={() => setLeftCollapsed(true)}
                className="
                  absolute
                  right-0
                  top-1/2
                  -translate-y-1/2
                  translate-x-1/2
                  z-50
                  flex
                  h-9
                  w-6
                  items-center
                  justify-center
                  rounded-r-lg
                  rounded-l-sm
                  border
                  border-cyan-400/30
                  bg-[#06131d]/95
                  text-cyan-300
                  shadow-[0_0_15px_rgba(0,200,255,0.18)]
                  transition-all
                  hover:bg-cyan-400/10
                  hover:text-cyan-200
                "
                title="Collapse control panel"
              >
                <ChevronLeft size={14} />
              </button>

            </div>

          </div>

        ) : (

          /* COLLAPSED LEFT TAB */

          <button
            onClick={() => setLeftCollapsed(false)}
            className="
              pointer-events-auto
              absolute
              left-0
              top-1/2
              -translate-y-1/2
              z-40
              flex
              h-12
              w-7
              items-center
              justify-center
              rounded-r-lg
              border
              border-cyan-400/30
              bg-[#06131d]/95
              text-cyan-300
              shadow-[0_0_20px_rgba(0,200,255,0.20)]
              transition-all
              hover:bg-cyan-400/10
            "
            title="Open control panel"
          >
            <ChevronRight size={16} />
          </button>

        )}


        {/* =======================================================
            RIGHT EVENT INTELLIGENCE
            COLLAPSIBLE
           ======================================================= */}

        {!rightCollapsed ? (

          <div className="pointer-events-auto absolute right-4 top-28 z-30 w-[360px]">

            <div className="relative rounded-2xl border border-cyan-400/25 bg-[#06101a]/80 p-2 backdrop-blur-2xl shadow-[0_0_35px_rgba(0,180,255,0.12)]">

              <EventIntelligence
                event={selectedEvent}
              />

              {/* COLLAPSE BUTTON */}

              <button
                onClick={() => setRightCollapsed(true)}
                className="
                  absolute
                  left-0
                  top-1/2
                  -translate-x-1/2
                  -translate-y-1/2
                  z-50
                  flex
                  h-9
                  w-6
                  items-center
                  justify-center
                  rounded-l-lg
                  rounded-r-sm
                  border
                  border-cyan-400/30
                  bg-[#06131d]/95
                  text-cyan-300
                  shadow-[0_0_15px_rgba(0,200,255,0.18)]
                  transition-all
                  hover:bg-cyan-400/10
                  hover:text-cyan-200
                "
                title="Collapse event intelligence"
              >
                <ChevronRight size={14} />
              </button>

            </div>

          </div>

        ) : (

          /* COLLAPSED RIGHT TAB */

          <button
            onClick={() => setRightCollapsed(false)}
            className="
              pointer-events-auto
              absolute
              right-0
              top-1/2
              -translate-y-1/2
              z-40
              flex
              h-12
              w-7
              items-center
              justify-center
              rounded-l-lg
              border
              border-cyan-400/30
              bg-[#06131d]/95
              text-cyan-300
              shadow-[0_0_20px_rgba(0,200,255,0.20)]
              transition-all
              hover:bg-cyan-400/10
            "
            title="Open event intelligence"
          >
            <ChevronLeft size={16} />
          </button>

        )}


        {/* =======================================================
            BOTTOM ANALYTICS DOCK
            COLLAPSIBLE
           ======================================================= */}

        {!bottomCollapsed ? (

          <div className="pointer-events-auto absolute bottom-4 left-1/2 z-30 w-[min(1100px,72vw)] -translate-x-1/2">

            <div className="relative rounded-2xl border border-cyan-400/20 bg-[#06101a]/75 p-2 backdrop-blur-2xl shadow-[0_0_35px_rgba(0,180,255,0.10)]">

              <AnalyticsCharts
                filtered={filtered}
              />

              {/* COLLAPSE BUTTON */}

              <button
                onClick={() => setBottomCollapsed(true)}
                className="
                  absolute
                  left-1/2
                  top-0
                  -translate-x-1/2
                  -translate-y-1/2
                  z-50
                  flex
                  h-6
                  w-12
                  items-center
                  justify-center
                  rounded-t-lg
                  border
                  border-cyan-400/30
                  bg-[#06131d]/95
                  text-cyan-300
                  shadow-[0_0_15px_rgba(0,200,255,0.18)]
                  transition-all
                  hover:bg-cyan-400/10
                  hover:text-cyan-200
                "
                title="Collapse analytics"
              >
                <ChevronDown size={15} />
              </button>

            </div>

          </div>

        ) : (

          /* COLLAPSED BOTTOM TAB */

          <button
            onClick={() => setBottomCollapsed(false)}
            className="
              pointer-events-auto
              absolute
              bottom-0
              left-1/2
              -translate-x-1/2
              z-40
              flex
              h-7
              w-14
              items-center
              justify-center
              rounded-t-lg
              border
              border-cyan-400/30
              bg-[#06131d]/95
              text-cyan-300
              shadow-[0_0_20px_rgba(0,200,255,0.20)]
              transition-all
              hover:bg-cyan-400/10
            "
            title="Open analytics"
          >
            <ChevronUp size={16} />
          </button>

        )}

      </div>

    </div>
  );
}
