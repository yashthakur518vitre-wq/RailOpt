from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.base import Base

class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(String, unique=True, index=True, nullable=False)
    corridor_id = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    source = Column(String, nullable=False)
    department = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    plan_id = Column(String, nullable=True)
