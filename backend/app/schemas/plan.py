from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from .block import BlockResponse

class PlanBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    plan_id: str
    horizon: str
    generated_at: datetime
    status: str
    objective_score: float
    total_tasks: int
    scheduled_tasks: int
    unscheduled_tasks: int
    total_block_hours: float
    estimated_availability_proxy: float
    train_impact_score: float
    maintenance_completion: float
    coordination_score: float
    validation_status: str
    model_versions: str

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    status: Optional[str] = None

class PlanResponse(PlanBase):
    id: int
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class PlanComparison(BaseModel):
    plan_a_id: str
    plan_b_id: str
    diff_metrics: Dict[str, Any]

class PlanApproval(BaseModel):
    plan_id: str
    approved: bool
    comments: Optional[str] = None

class GeneratePlanRequest(BaseModel):
    corridor_ids: List[str]
    horizon: str
    target_date: str
    weights: Optional[Dict[str, float]] = None

class GeneratePlanResponse(BaseModel):
    plan: PlanResponse
    scheduled_tasks: List[Any]
    unscheduled_tasks: List[Any]
    blocks: List[BlockResponse]
    kpis: Dict[str, Any]
    baseline_comparison: Dict[str, Any]
    validation: Dict[str, Any]
