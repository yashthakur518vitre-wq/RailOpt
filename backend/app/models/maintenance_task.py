from sqlalchemy import Column, Integer, String, Float, Date
from app.database.base import Base

class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    asset_id = Column(String, nullable=False)
    department = Column(String, nullable=False)
    task_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    estimated_duration = Column(Float, nullable=False)
    required_block_duration = Column(Float, nullable=False)
    criticality = Column(String, nullable=False)
    urgency = Column(String, nullable=False)
    safety_impact = Column(String, nullable=False)
    asset_impact = Column(String, nullable=False)
    status = Column(String, nullable=False)
    required_resources = Column(String, nullable=False)
    preferred_time_window = Column(String, nullable=False)
    corridor_id = Column(String, nullable=False)
    dependency_task_id = Column(String, nullable=True)
    
    # AI Enrichment Fields
    ai_priority_score = Column(Float, nullable=True)
    ai_priority_level = Column(String, nullable=True)
    ai_failure_risk = Column(Float, nullable=True)
    ai_risk_percentage = Column(Float, nullable=True)
    ai_train_impact_score = Column(Float, nullable=True)
    ai_reasons = Column(String, nullable=True) # JSON string
    ai_model_version = Column(String, nullable=True)
