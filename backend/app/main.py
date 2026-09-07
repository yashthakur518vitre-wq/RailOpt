import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.database.database import init_db
from app.api.routes import dashboard, assets, maintenance, defects, corridors, trains, blocks, planning, analytics, ai, demo, resources


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    os.makedirs(settings.MODEL_DIR, exist_ok=True)
    try:
        maintenance.predictor.initialize()
    except Exception:
        pass
    try:
        ai.predictor.initialize()
    except Exception:
        pass
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="RailBlock AI Backend API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS configuration
origins = [origin.strip() for origin in settings.FRONTEND_ORIGINS.split(',') if origin.strip()]
# Also allow private-LAN Vite origins so the dashboard can be opened from a phone/tablet
# on the same network during an SIH demo.
allow_origin_regex = r"^https?://(localhost|127\.0.0.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})(?::\d+)?$"
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": str(exc)}}
    )

app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["maintenance"])
app.include_router(defects.router, prefix="/api/defects", tags=["defects"])
app.include_router(corridors.router, prefix="/api/corridors", tags=["corridors"])
app.include_router(trains.router, prefix="/api/trains", tags=["trains"])
app.include_router(blocks.router, prefix="/api/blocks", tags=["blocks"])
app.include_router(planning.router, prefix="/api/planning", tags=["planning"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(demo.router, prefix="/api/demo", tags=["demo"])
app.include_router(resources.router, prefix="/api/resources", tags=["resources"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}

@app.get("/health/database")
def database_health():
    from app.database.database import SessionLocal
    from app.models import Asset, MaintenanceTask, Block, Train, Corridor, Resource, Defect, Plan
    db = SessionLocal()
    try:
        counts = {
            "assets": db.query(Asset).count(),
            "maintenance_tasks": db.query(MaintenanceTask).count(),
            "blocks": db.query(Block).count(),
            "trains": db.query(Train).count(),
            "corridors": db.query(Corridor).count(),
            "resources": db.query(Resource).count(),
            "defects": db.query(Defect).count(),
            "plans": db.query(Plan).count(),
        }
        return {"status": "ok", "database": settings.DATABASE_URL, "counts": counts}
    finally:
        db.close()
