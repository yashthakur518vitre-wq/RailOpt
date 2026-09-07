from sqlalchemy import Column, Integer, String, Float, Date
from app.database.base import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String, unique=True, index=True, nullable=False)
    asset_type = Column(String, nullable=False)
    department = Column(String, nullable=False)
    location = Column(String, nullable=False)
    corridor_id = Column(String, nullable=False)
    criticality = Column(String, nullable=False)
    installation_date = Column(Date, nullable=False)
    last_maintenance_date = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=False)
    condition_score = Column(Float, nullable=False)
    availability_status = Column(String, nullable=False)
    failure_history = Column(Integer, default=0)
