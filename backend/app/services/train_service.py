from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models import Train

class TrainService:
    @staticmethod
    def get_all_trains(db: Session) -> List[Train]:
        return db.query(Train).all()

    @staticmethod
    def create_train(db: Session, train_data: Dict[str, Any]) -> Train:
        db_train = Train(**train_data)
        db.add(db_train)
        db.commit()
        db.refresh(db_train)
        return db_train

    @staticmethod
    def get_trains_by_corridor(db: Session, corridor_id: str) -> List[Train]:
        return db.query(Train).filter(Train.corridor_id == corridor_id).all()

    @staticmethod
    def get_train_forecast(db: Session) -> List[Train]:
        return db.query(Train).filter(Train.forecasted == True, Train.train_type == 'Goods').all()

    @staticmethod
    def calculate_train_density(db: Session, corridor_id: str) -> float:
        count = db.query(Train).filter(Train.corridor_id == corridor_id).count()
        return float(count)
