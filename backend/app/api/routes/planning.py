from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.planning_service import PlanningService
from app.schemas.common import APIResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=APIResponse)
def generate_plan(horizon: str = Query("weekly", pattern="^(weekly|monthly)$"), db: Session = Depends(get_db)):
    try:
        result = PlanningService.generate_plan(db, horizon)
        return APIResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Error generating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=APIResponse)
def get_plans(db: Session = Depends(get_db)):
    plans = PlanningService.get_all_plans(db)
    return APIResponse(success=True, data=plans)

@router.get("/{plan_id}", response_model=APIResponse)
def get_plan(plan_id: str, db: Session = Depends(get_db)):
    plan_details = PlanningService.get_plan(db, plan_id)
    if not plan_details:
        raise HTTPException(status_code=404, detail="Plan not found")
    return APIResponse(success=True, data=plan_details)

@router.post("/{plan_id}/approve", response_model=APIResponse)
def approve_plan(plan_id: str, db: Session = Depends(get_db)):
    plan = PlanningService.approve_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return APIResponse(success=True, data=plan)

@router.post("/{plan_id}/regenerate", response_model=APIResponse)
def regenerate_plan(plan_id: str, db: Session = Depends(get_db)):
    try:
        result = PlanningService.regenerate_plan(db, plan_id)
        if not result:
            raise HTTPException(status_code=404, detail="Plan not found")
        return APIResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Error regenerating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
