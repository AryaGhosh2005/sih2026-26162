from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.analytics import router as analytics_router
from api.exports import router as exports_router
from api.fires import router as fires_router
from api.industries import router as industries_router
from api.risk import router as risk_router


app = FastAPI(
    title="Industrial Fire Detection API",
    description=(
        "Satellite thermal intelligence platform for "
        "industrial fire detection, classification, "
        "and risk assessment."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(fires_router)
app.include_router(risk_router)
app.include_router(industries_router)
app.include_router(analytics_router)
app.include_router(exports_router)


@app.get("/")
def root():
    return {
        "system": "SIH 26162 Industrial Fire Detection System",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "industrial-fire-detection-backend",
    }
