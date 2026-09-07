from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import Defect
from app.schemas.defect import DefectCreate
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("", response_model=APIResponse)
def get_defects(db: Session = Depends(get_db)):
    defects = db.query(Defect).all()
    return APIResponse(success=True, data=defects)

@router.post("", response_model=APIResponse)
def create_defect(defect: DefectCreate, db: Session = Depends(get_db)):
    new_defect = Defect(**defect.model_dump())
    db.add(new_defect)
    db.commit()
    db.refresh(new_defect)
    return APIResponse(success=True, data=new_defect)
