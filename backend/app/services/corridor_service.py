from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from app.models import Corridor, Train, Block

class CorridorService:
    @staticmethod
    def get_all_corridors(db: Session) -> List[Corridor]:
        return db.query(Corridor).all()

    @staticmethod
    def get_corridor(db: Session, corridor_id: str) -> Optional[Corridor]:
        return db.query(Corridor).filter(Corridor.corridor_id == corridor_id).first()

    @staticmethod
    def get_availability_windows(db: Session, corridor_id: str) -> List[Dict[str, Any]]:
        corridor = CorridorService.get_corridor(db, corridor_id)
        if not corridor or not corridor.availability_windows:
            return []
        try:
            return json.loads(corridor.availability_windows)
        except json.JSONDecodeError:
            return []

    @staticmethod
    def get_corridor_utilization(db: Session, corridor_id: str) -> Dict[str, Any]:
        corridor = CorridorService.get_corridor(db, corridor_id)
        if not corridor:
            return {}
        trains = db.query(Train).filter(Train.corridor_id == corridor_id).count()
        blocks = db.query(Block).filter(Block.corridor_id == corridor_id).count()
        return {
            "corridor_id": corridor_id,
            "capacity": corridor.capacity,
            "trains_count": trains,
            "blocks_count": blocks
        }
