from pydantic import BaseModel, ConfigDict
from typing import Optional

class CorridorBase(BaseModel):
    corridor_id: str
    name: str
    start_station: str
    end_station: str
    distance_km: float
    route_type: str
    capacity: int
    availability_windows: str

class CorridorCreate(CorridorBase):
    pass

class CorridorUpdate(BaseModel):
    capacity: Optional[int] = None
    availability_windows: Optional[str] = None

class CorridorResponse(CorridorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
