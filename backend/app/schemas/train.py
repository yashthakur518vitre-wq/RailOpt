from pydantic import BaseModel, ConfigDict
from typing import Optional

class TrainBase(BaseModel):
    train_id: str
    train_number: str
    train_type: str
    origin: str
    destination: str
    corridor_id: str
    arrival_time: str
    departure_time: str
    frequency: str
    priority: str
    occupancy: float
    forecasted: bool

class TrainCreate(TrainBase):
    pass

class TrainUpdate(BaseModel):
    occupancy: Optional[float] = None
    forecasted: Optional[bool] = None

class TrainResponse(TrainBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TrainForecast(BaseModel):
    train_id: str
    predicted_delay: float
    confidence: float
