from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("/asset-availability", response_model=APIResponse)
def get_asset_availability(db: Session = Depends(get_db)):
    data = AnalyticsService.get_asset_availability(db)
    return APIResponse(success=True, data=data)

@router.get("/maintenance-completion", response_model=APIResponse)
def get_maintenance_completion(db: Session = Depends(get_db)):
    data = AnalyticsService.get_maintenance_completion(db)
    return APIResponse(success=True, data=data)

@router.get("/train-impact", response_model=APIResponse)
def get_train_impact(db: Session = Depends(get_db)):
    data = AnalyticsService.get_train_impact(db)
    return APIResponse(success=True, data=data)

@router.get("/department-performance", response_model=APIResponse)
def get_department_performance(db: Session = Depends(get_db)):
    data = AnalyticsService.get_department_performance(db)
    return APIResponse(success=True, data=data)
