from sqlalchemy import Column, Integer, String, Float
from app.database.base import Base

class Corridor(Base):
    __tablename__ = "corridors"

    id = Column(Integer, primary_key=True, index=True)
    corridor_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    start_station = Column(String, nullable=False)
    end_station = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    route_type = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    availability_windows = Column(String, nullable=False) # JSON string
