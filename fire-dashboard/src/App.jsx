import React, { useEffect, useMemo, useState, useCallback } from "react";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import KpiCards from "./components/KpiCards";
import FireMap from "./components/FireMap";
import EventIntelligence from "./components/EventIntelligence";
import AnalyticsCharts from "./components/AnalyticsCharts";
import RecentIncidents from "./components/RecentIncidents";
import Reports from "./components/Reports";
import { loadData } from "./api";
import { applyFilters, toDateOnly } from "./utils";
import { RISK_OPTIONS, SOURCE_TYPES } from "./constants";

function defaultFilters(fires) {
  const dates = fires.map((f) => toDateOnly(f.acquisition_date)).filter(Boolean);
  const startDate = dates.length ? dates.reduce((a, b) => (a < b ? a : b)) : toDateOnly(new Date());
  const endDate = dates.length ? dates.reduce((a, b) => (a > b ? a : b)) : toDateOnly(new Date());

  const distances = fires.map((f) => Number(f.distance_to_industry)).filter((n) => !Number.isNaN(n));
  const dataMaxDistance = distances.length ? Math.floor(Math.max(...distances)) + 1 : 2000;

  const satellites = [...new Set(fires.map((f) => String(f.satellite)))].sort();

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
    // Auto-refresh every 5 minutes, matching the "Every 5 min" status chip.
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

  if (loading && !filters) {
    return (
      <div className="min-h-screen flex items-center justify-center text-[#8490a2] text-sm">
        Loading fire detection data…
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="bg-[#0c1622] border border-[#24354a] rounded-md text-[#f5a3a3] text-sm px-4 py-3 max-w-lg">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <div className="w-[260px] shrink-0">
        <Sidebar
          filters={filters}
          setFilters={setFilters}
          dataStatus={{ total: fires.length }}
          onRefresh={() => setRefreshKey((k) => k + 1)}
          satellites={satellites}
        />
      </div>

      <main className="flex-1 px-5 py-3.5 max-w-full space-y-1">
        <Header />
        <KpiCards filtered={filtered} allFires={fires} />

        <div className="flex items-center gap-2 text-[#dbe3ee] text-[11px] font-bold tracking-wider mt-3.5 mb-2">
          LIVE FIRE MONITORING
          <span className="flex-1 h-px bg-[#161f2c]" />
        </div>
        <div className="grid grid-cols-[3.5fr_1.15fr] gap-3">
          <FireMap fires={filtered} industries={industries} onSelectEvent={setSelectedEvent} />
          <EventIntelligence event={selectedEvent} />
        </div>

        <AnalyticsCharts filtered={filtered} />
        <RecentIncidents filtered={filtered} />
        <Reports filtered={filtered} />

        <div className="text-center text-[#4e5c70] text-[8px] py-4">
          INDUSTRIAL FIRE DETECTION SYSTEM &middot; NASA FIRMS &middot; OSM &middot; Satellite Thermal Intelligence &middot; SIH 26162
        </div>
      </main>
    </div>
  );
}
