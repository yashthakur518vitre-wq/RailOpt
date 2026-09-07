from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.train_service import TrainService
from app.schemas.common import APIResponse
from app.schemas.train import TrainCreate

router = APIRouter()

@router.get("", response_model=APIResponse)
def get_trains(db: Session = Depends(get_db)):
    return APIResponse(success=True, data=TrainService.get_all_trains(db))

@router.get("/forecast", response_model=APIResponse)
def get_train_forecast(db: Session = Depends(get_db)):
    return APIResponse(success=True, data=TrainService.get_train_forecast(db))

@router.post("", response_model=APIResponse)
def create_train(train: TrainCreate, db: Session = Depends(get_db)):
    return APIResponse(success=True, data=TrainService.create_train(db, train.model_dump()))
