from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.corridor_service import CorridorService
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("", response_model=APIResponse)
def get_corridors(db: Session = Depends(get_db)):
    corridors = CorridorService.get_all_corridors(db)
    return APIResponse(success=True, data=corridors)

@router.get("/{corridor_id}", response_model=APIResponse)
def get_corridor(corridor_id: str, db: Session = Depends(get_db)):
    corridor = CorridorService.get_corridor(db, corridor_id)
    if not corridor:
        raise HTTPException(status_code=404, detail="Corridor not found")
    windows = CorridorService.get_availability_windows(db, corridor_id)
    return APIResponse(success=True, data={"corridor": corridor, "availability_windows": windows})
