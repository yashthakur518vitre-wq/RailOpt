from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.base import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String, unique=True, index=True, nullable=False)
    horizon = Column(String, nullable=False)
    generated_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    objective_score = Column(Float, nullable=False)
    total_tasks = Column(Integer, nullable=False)
    scheduled_tasks = Column(Integer, nullable=False)
    unscheduled_tasks = Column(Integer, nullable=False)
    total_block_hours = Column(Float, nullable=False)
    estimated_availability_proxy = Column(Float, nullable=False)
    train_impact_score = Column(Float, nullable=False)
    maintenance_completion = Column(Float, nullable=False)
    coordination_score = Column(Float, nullable=False)
    validation_status = Column(String, nullable=False) # JSON
    model_versions = Column(String, nullable=False) # JSON
