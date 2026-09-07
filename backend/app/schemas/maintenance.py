from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class AIEnrichment(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    priority_score: float
    priority_level: str
    failure_risk: float
    risk_percentage: float
    train_impact_score: float
    reasons: str
    model_version: str

class MaintenanceTaskBase(BaseModel):
    task_id: str
    asset_id: str
    department: str
    task_type: str
    description: str
    created_date: date
    due_date: date
    estimated_duration: float
    required_block_duration: float
    criticality: str
    urgency: str
    safety_impact: str
    asset_impact: str
    status: str
    required_resources: str
    preferred_time_window: str
    corridor_id: str
    dependency_task_id: Optional[str] = None
    
    ai_priority_score: Optional[float] = None
    ai_priority_level: Optional[str] = None
    ai_failure_risk: Optional[float] = None
    ai_risk_percentage: Optional[float] = None
    ai_train_impact_score: Optional[float] = None
    ai_reasons: Optional[str] = None
    ai_model_version: Optional[str] = None

class MaintenanceTaskCreate(MaintenanceTaskBase):
    pass

class MaintenanceTaskUpdate(BaseModel):
    status: Optional[str] = None
    dependency_task_id: Optional[str] = None
    # Add other fields as optional

class MaintenanceTaskResponse(MaintenanceTaskBase):
    id: int
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
