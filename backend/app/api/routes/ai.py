from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.ai.predictor import RailBlockPredictor
from app.ai.model_manager import ModelManager
from app.services.maintenance_service import MaintenanceService
from app.models import Asset, Defect
from app.schemas.common import APIResponse

router = APIRouter()
predictor = RailBlockPredictor()
manager = ModelManager()

@router.get("/priority/{task_id}", response_model=APIResponse)
def get_priority(task_id: str, db: Session = Depends(get_db)):
    task = MaintenanceService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    enriched = MaintenanceService.enrich_task_with_ai(db, task, predictor)
    return APIResponse(success=True, data=enriched["ai_enrichment"])

@router.get("/priorities/top", response_model=APIResponse)
def get_top_priorities(limit: int = 10, db: Session = Depends(get_db)):
    # Fetch top pending tasks
    from app.models import MaintenanceTask
    tasks = db.query(MaintenanceTask).filter(MaintenanceTask.status.in_(['PENDING', 'OVERDUE'])).limit(limit).all()
    results = []
    for t in tasks:
        try:
            enriched = MaintenanceService.enrich_task_with_ai(db, t, predictor)
            results.append({
                "task_id": t.task_id,
                "task_type": t.task_type,
                "department": t.department,
                "priority_score": enriched["ai_enrichment"].get("priority_score"),
                "criticality": enriched["ai_enrichment"].get("criticality_prediction"),
                "urgency": enriched["ai_enrichment"].get("urgency_prediction")
            })
        except Exception:
            continue
    # sort by priority
    results.sort(key=lambda x: x.get('priority_score', 0) or 0, reverse=True)
    return APIResponse(success=True, data=results)

@router.get("/risk/{asset_id}", response_model=APIResponse)
def get_risk(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    defects = db.query(Defect).filter(Defect.asset_id == asset_id).all()
    
    asset_dict = {c.name: getattr(asset, c.name) for c in asset.__table__.columns}
    defects_dict = [{c.name: getattr(d, c.name) for c in d.__table__.columns} for d in defects]
    
    try:
        risk = predictor.predict_risk(asset_dict, defects_dict)
        return APIResponse(success=True, data=risk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-impact", response_model=APIResponse)
def predict_impact(payload: dict = Body(...), db: Session = Depends(get_db)):
    from app.models import Corridor, Train
    corridor_id = payload.get('corridor_id')
    block_duration = payload.get('block_duration', 1.0)
    block_start_hour = payload.get('block_start_hour', 12)
    
    corridor = db.query(Corridor).filter(Corridor.corridor_id == corridor_id).first()
    if not corridor:
        raise HTTPException(status_code=404, detail="Corridor not found")
        
    trains = db.query(Train).filter(Train.corridor_id == corridor_id).all()
    corridor_dict = {c.name: getattr(corridor, c.name) for c in corridor.__table__.columns}
    trains_dict = [{c.name: getattr(t, c.name) for c in t.__table__.columns} for t in trains]
    
    try:
        impact = predictor.predict_impact(corridor_dict, trains_dict, float(block_duration), int(block_start_hour))
        return APIResponse(success=True, data=impact)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-status", response_model=APIResponse)
def get_model_status():
    status = manager.get_model_status()
    return APIResponse(success=True, data=status)
