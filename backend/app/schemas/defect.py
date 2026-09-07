from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class DefectBase(BaseModel):
    defect_id: str
    asset_id: str
    department: str
    severity: str
    detected_date: date
    description: str
    failure_probability: float
    safety_impact: str
    operational_impact: str
    status: str

class DefectCreate(DefectBase):
    pass

class DefectUpdate(BaseModel):
    severity: Optional[str] = None
    status: Optional[str] = None

class DefectResponse(DefectBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
