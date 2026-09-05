import React, { useEffect, useMemo, useState, useCallback } from "react";
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

  const satellites = useMemo(
    () => [...new Set(fires.map((f) => String(f.satellite)))].sort(),
    [fires]
  );

  const filtered = useMemo(() => {
    if (!filters) return [];

    return applyFilters(fires, filters);
  }, [fires, filters]);

  useEffect(() => {
    if (filtered.length && !filtered.includes(selectedEvent)) {
      setSelectedEvent(filtered[0]);
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
          FireMap itself is NOT being modified.
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

                <div className="text-[11px] font-medium tracking-[0.2em] text-cyan-300">
                  DETECTION SYSTEM
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
    Positioned away from Leaflet map controls
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
      {new Date().toLocaleTimeString()}
    </div>

    <div className="text-[8px] text-slate-500 whitespace-nowrap">
      {new Date().toLocaleDateString()}
    </div>

  </div>

</div>

        {/* =======================================================
            FLOATING CONTROL PANEL
           ======================================================= */}
        <div className="pointer-events-auto absolute bottom-24 left-4 top-28 z-30 w-[220px]">

          <div className="h-full overflow-hidden rounded-2xl border border-cyan-400/20 bg-[#050b13]/75 backdrop-blur-2xl shadow-[0_0_35px_rgba(0,200,255,0.08)]">

            <Sidebar
              filters={filters}
              setFilters={setFilters}
              dataStatus={{ total: fires.length }}
              onRefresh={() => setRefreshKey((k) => k + 1)}
              satellites={satellites}
            />

          </div>

        </div>


        {/* =======================================================
            EVENT INTELLIGENCE
           ======================================================= */}
        <div className="pointer-events-auto absolute right-4 top-28 z-30 w-[360px]">

          <div className="rounded-2xl border border-cyan-400/25 bg-[#06101a]/80 p-2 backdrop-blur-2xl shadow-[0_0_35px_rgba(0,180,255,0.12)]">

            <EventIntelligence
              event={selectedEvent}
            />

          </div>

        </div>


        {/* =======================================================
            ANALYTICS DOCK
           ======================================================= */}
        <div className="pointer-events-auto absolute bottom-4 left-1/2 z-30 w-[min(1100px,72vw)] -translate-x-1/2">

          <div className="rounded-2xl border border-cyan-400/20 bg-[#06101a]/75 p-2 backdrop-blur-2xl shadow-[0_0_35px_rgba(0,180,255,0.10)]">

            <AnalyticsCharts
              filtered={filtered}
            />

          </div>

        </div>

      </div>

    </div>
  );
}
