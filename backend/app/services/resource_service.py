from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models import Resource


class ResourceService:
    @staticmethod
    def get_all_resources(db: Session) -> List[Resource]:
        return db.query(Resource).all()

    @staticmethod
    def get_resources_by_department(db: Session, department: str) -> List[Resource]:
        return db.query(Resource).filter(Resource.department == department).all()

    @staticmethod
    def create_resource(db: Session, resource_data: Dict[str, Any]) -> Resource:
        db_resource = Resource(**resource_data)
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        return db_resource
