from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BlockBase(BaseModel):
    block_id: str
    corridor_id: str
    start_time: datetime
    end_time: datetime
    duration: float
    status: str
    source: str
    department: str
    reason: str
    plan_id: Optional[str] = None

class BlockCreate(BlockBase):
    pass

class BlockUpdate(BaseModel):
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None

class BlockResponse(BlockBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
