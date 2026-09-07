from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.analytics_service import AnalyticsService
from app.models import MaintenanceTask, Block
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("/summary", response_model=APIResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    kpis = AnalyticsService.calculate_kpis(db)
    recent_tasks = db.query(MaintenanceTask).order_by(MaintenanceTask.created_date.desc()).limit(5).all()
    active_blocks = db.query(Block).filter(Block.status == "APPROVED").limit(5).all()
    
    return APIResponse(
        success=True,
        data={
            "kpis": kpis,
            "recent_tasks": recent_tasks,
            "active_blocks": active_blocks
        }
    )

@router.get("/kpis", response_model=APIResponse)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    kpis = AnalyticsService.calculate_kpis(db)
    return APIResponse(
        success=True,
        data=kpis
    )
