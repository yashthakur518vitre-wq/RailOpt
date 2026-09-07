from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class AssetBase(BaseModel):
    asset_id: str
    asset_type: str
    department: str
    location: str
    corridor_id: str
    criticality: str
    installation_date: date
    last_maintenance_date: date
    next_due_date: date
    condition_score: float
    availability_status: str
    failure_history: int

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    asset_type: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    corridor_id: Optional[str] = None
    criticality: Optional[str] = None
    installation_date: Optional[date] = None
    last_maintenance_date: Optional[date] = None
    next_due_date: Optional[date] = None
    condition_score: Optional[float] = None
    availability_status: Optional[str] = None
    failure_history: Optional[int] = None

class AssetResponse(AssetBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
