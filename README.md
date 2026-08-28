# SIH 26162 Backend

FastAPI + Pydantic backend for the Industrial Fire Detection System.

## Structure

```text
backend/
├── main.py
├── requirements.txt
├── api/
├── schemas/
├── services/
└── data/
```

## Data location

The code expects the repository-level data directory:

```text
sih2026-26162/
├── data/
│   ├── classified_fires.csv
│   └── industries.csv
└── backend/
```

If those files already exist in the repository `data/` folder, do not duplicate them.

## Run locally

From the repository root:

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload
```

API:
- http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/api/v1/health

## Main endpoints

- `GET /api/v1/fires`
- `GET /api/v1/fires/{fire_id}`
- `GET /api/v1/risk/{fire_id}`
- `GET /api/v1/industries`
- `GET /api/v1/industries/{industry_id}`
- `GET /api/v1/analytics/summary`
- `GET /api/v1/analytics/daily-trend`
- `GET /api/v1/export/csv`
- `GET /api/v1/export/geojson`

## Important

This version uses CSV files as the data layer so it can be integrated with the current prototype immediately. PostgreSQL/PostGIS can be added later without changing the API contract.
