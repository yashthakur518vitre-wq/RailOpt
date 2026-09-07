from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database.base import Base

class Train(Base):
    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(String, unique=True, index=True, nullable=False)
    train_number = Column(String, nullable=False)
    train_type = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    corridor_id = Column(String, nullable=False)
    arrival_time = Column(String, nullable=False) # HH:MM
    departure_time = Column(String, nullable=False) # HH:MM
    frequency = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    occupancy = Column(Float, nullable=False)
    forecasted = Column(Boolean, default=False)
