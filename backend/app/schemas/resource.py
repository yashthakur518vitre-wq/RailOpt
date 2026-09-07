from pydantic import BaseModel, ConfigDict
from typing import Optional


class ResourceBase(BaseModel):
    resource_id: str
    name: str
    department: str
    capability: str
    availability: str
    quantity: int


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    capability: Optional[str] = None
    availability: Optional[str] = None
    quantity: Optional[int] = None


class ResourceResponse(ResourceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
