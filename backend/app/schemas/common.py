from typing import Optional, Any, List
from pydantic import BaseModel, model_validator

def _to_dict(obj):
    if isinstance(obj, list):
        return [_to_dict(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    if hasattr(obj, '__table__'):
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    return obj

class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[Any]


class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None

    model_config = {"from_attributes": True}

    @model_validator(mode='before')
    @classmethod
    def serialize_data(cls, values):
        if isinstance(values, dict) and 'data' in values and values['data'] is not None:
            values['data'] = _to_dict(values['data'])
        elif hasattr(values, 'data') and values.data is not None:
            values.data = _to_dict(values.data)
        return values


class ErrorResponse(BaseModel):
    success: bool = False
    error: Optional[dict] = None


class KPIResponse(BaseModel):
    name: str
    value: float
    unit: str
    trend: Optional[str] = None
