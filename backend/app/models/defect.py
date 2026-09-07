from sqlalchemy import Column, Integer, String, Float, Date
from app.database.base import Base

class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)
    defect_id = Column(String, unique=True, index=True, nullable=False)
    asset_id = Column(String, nullable=False)
    department = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    detected_date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    failure_probability = Column(Float, nullable=False)
    safety_impact = Column(String, nullable=False)
    operational_impact = Column(String, nullable=False)
    status = Column(String, nullable=False)
