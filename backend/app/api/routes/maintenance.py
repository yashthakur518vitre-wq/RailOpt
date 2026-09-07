from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.maintenance_service import MaintenanceService
from app.ai.predictor import RailBlockPredictor
from app.schemas.maintenance import MaintenanceTaskCreate, MaintenanceTaskUpdate
from app.schemas.common import APIResponse

router = APIRouter()
predictor = RailBlockPredictor()

@router.get("", response_model=APIResponse)
def get_tasks(department: str = None, status: str = None, criticality: str = None, db: Session = Depends(get_db)):
    filters = {}
    if department: filters['department'] = department
    if status: filters['status'] = status
    if criticality: filters['criticality'] = criticality
    tasks = MaintenanceService.get_all_tasks(db, filters)
    return APIResponse(success=True, data=tasks)

@router.get("/{task_id}", response_model=APIResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = MaintenanceService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    enriched = MaintenanceService.enrich_task_with_ai(db, task, predictor)
    return APIResponse(success=True, data=enriched)

@router.post("", response_model=APIResponse)
def create_task(task: MaintenanceTaskCreate, db: Session = Depends(get_db)):
    new_task = MaintenanceService.create_task(db, task.model_dump())
    return APIResponse(success=True, data=new_task)

@router.put("/{task_id}", response_model=APIResponse)
def update_task(task_id: str, task: MaintenanceTaskUpdate, db: Session = Depends(get_db)):
    updated_task = MaintenanceService.update_task(db, task_id, task.model_dump(exclude_unset=True))
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return APIResponse(success=True, data=updated_task)
