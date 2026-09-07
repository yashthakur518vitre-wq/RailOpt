from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.resource_service import ResourceService
from app.schemas.common import APIResponse
from app.schemas.resource import ResourceCreate

router = APIRouter()


@router.get("", response_model=APIResponse)
def get_resources(db: Session = Depends(get_db)):
    resources = ResourceService.get_all_resources(db)
    return APIResponse(success=True, data=resources)


@router.post("", response_model=APIResponse)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    new_resource = ResourceService.create_resource(db, resource.model_dump())
    return APIResponse(success=True, data=new_resource)
