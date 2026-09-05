# Industrial Fire Detection System — React Frontend

React + Vite port of the Streamlit dashboard (`app.py` + `map_visualization.py`,
SIH 26162). Talks to the **same FastAPI backend** — no backend changes needed.

## What's included

- **Header** — logo, live clock, system status (`Header.jsx`)
- **Sidebar filters** — date range, risk level, source type, confidence,
  thermal intensity, industrial proximity, satellite, data status, manual
  refresh (`Sidebar.jsx`)
- **KPI cards** — active events, high risk, persistent sources, industrial
  proximity, total detections, each with a "today" delta (`KpiCards.jsx`)
- **Live map** — Leaflet with satellite/OSM base layers, industrial facility
  markers, pulsing thermal-anomaly markers colored by classification, a
  toggleable heatmap, fullscreen, and glass-style popups with the same
  proximity/intensity/persistence/confidence breakdown as the sidebar panel
  (`FireMap.jsx`)
- **Event Intelligence** — detail card + "AI Explanation" bars for the
  selected/clicked event (`EventIntelligence.jsx`)
- **Analytics** — thermal activity (area), risk trend (line), source
  distribution (donut) via Recharts (`AnalyticsCharts.jsx`)
- **Recent Incidents** — top 4 events by risk score (`RecentIncidents.jsx`)
- **Reports** — CSV and GeoJSON export of the currently filtered rows
  (`Reports.jsx`)

`risk_score` / `risk_level` are read straight from the API response and are
**never recomputed in the frontend** — same rule the original app.py followed
(the popup breakdown percentages are illustrative UI only, exactly like the
"AI EXPLANATION" panel in the Streamlit version, and never feed back into the
risk score).

## Setup

```bash
npm install
cp .env.example .env   # adjust VITE_FIRE_API_BASE if your API isn't on :8000
npm run dev
```

Open the printed local URL (default `http://localhost:5173`).

## Backend requirement: CORS

Since the browser now calls your FastAPI backend directly (instead of
Streamlit's server-side `requests.get`), make sure the backend allows the
frontend's origin, e.g. in your FastAPI app:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Build for production

```bash
npm run build   # outputs to dist/
npm run preview # serve the production build locally
```

## Notes / things you may want to adjust

- The backend contract expected is unchanged: `GET /api/v1/fires` and
  `GET /api/v1/industries`, same shape as `data_service.load_fires()` /
  `load_industries()` in the original app — including `risk_score` and
  `risk_level` already computed by `risk_engine.py`.
- Auto-refresh every 5 minutes is wired up (matching the sidebar's
  "Auto-refresh: Every 5 min" chip); the "↻ REFRESH DATA" button forces an
  immediate refetch.
- The heatmap layer is off by default (same as the Streamlit version) — use
  the "🌡 Heatmap" button on the map to toggle it.
