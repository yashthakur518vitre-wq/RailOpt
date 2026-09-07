from sqlalchemy.orm import Session
from datetime import date
from typing import List, Dict, Any, Optional

from app.models import MaintenanceTask
from app.ai.predictor import RailBlockPredictor

class MaintenanceService:
    @staticmethod
    def get_all_tasks(db: Session, filters: Dict[str, Any] = None) -> List[MaintenanceTask]:
        query = db.query(MaintenanceTask)
        if filters:
            if filters.get("department"):
                query = query.filter(MaintenanceTask.department == filters["department"])
            if filters.get("status"):
                query = query.filter(MaintenanceTask.status == filters["status"])
            if filters.get("criticality"):
                query = query.filter(MaintenanceTask.criticality == filters["criticality"])
        return query.all()

    @staticmethod
    def get_task(db: Session, task_id: str) -> Optional[MaintenanceTask]:
        return db.query(MaintenanceTask).filter(MaintenanceTask.task_id == task_id).first()

    @staticmethod
    def create_task(db: Session, task_data: Dict[str, Any]) -> MaintenanceTask:
        task = MaintenanceTask(**task_data)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task(db: Session, task_id: str, update_data: Dict[str, Any]) -> Optional[MaintenanceTask]:
        task = db.query(MaintenanceTask).filter(MaintenanceTask.task_id == task_id).first()
        if task:
            for key, value in update_data.items():
                setattr(task, key, value)
            db.commit()
            db.refresh(task)
        return task

    @staticmethod
    def get_pending_tasks(db: Session) -> List[MaintenanceTask]:
        return db.query(MaintenanceTask).filter(MaintenanceTask.status.in_(["PENDING", "OVERDUE"])).all()

    @staticmethod
    def get_overdue_tasks(db: Session) -> List[MaintenanceTask]:
        return db.query(MaintenanceTask).filter(
            MaintenanceTask.status.in_(["PENDING", "OVERDUE"]),
            MaintenanceTask.due_date < date.today()
        ).all()

    @staticmethod
    def get_tasks_by_department(db: Session, department: str) -> List[MaintenanceTask]:
        return db.query(MaintenanceTask).filter(MaintenanceTask.department == department).all()

    @staticmethod
    def get_tasks_by_corridor(db: Session, corridor_id: str) -> List[MaintenanceTask]:
        return db.query(MaintenanceTask).filter(MaintenanceTask.corridor_id == corridor_id).all()

    @staticmethod
    def enrich_task_with_ai(db: Session, task: MaintenanceTask, predictor: RailBlockPredictor) -> Dict[str, Any]:
        # Implement logic for fetching asset, defects, trains, corridor to pass to predictor
        from app.models import Asset, Defect, Train, Corridor
        asset = db.query(Asset).filter(Asset.asset_id == task.asset_id).first()
        defects = db.query(Defect).filter(Defect.asset_id == task.asset_id).all()
        corridor = db.query(Corridor).filter(Corridor.corridor_id == task.corridor_id).first()
        trains = db.query(Train).filter(Train.corridor_id == task.corridor_id).all()
        
        task_dict = {c.name: getattr(task, c.name) for c in task.__table__.columns}
        asset_dict = {c.name: getattr(asset, c.name) for c in asset.__table__.columns} if asset else {}
        defects_dict = [{c.name: getattr(d, c.name) for c in d.__table__.columns} for d in defects]
        corridor_dict = {c.name: getattr(corridor, c.name) for c in corridor.__table__.columns} if corridor else {}
        trains_dict = [{c.name: getattr(t, c.name) for c in t.__table__.columns} for t in trains]
        
        pred = predictor.predict_priority(task_dict, asset_dict, defects_dict, trains_dict, corridor_dict)
        
        return {
            "task": task_dict,
            "ai_enrichment": pred
        }
