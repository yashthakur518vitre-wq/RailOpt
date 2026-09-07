from sqlalchemy import Column, Integer, String
from app.database.base import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    capability = Column(String, nullable=False)
    availability = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
