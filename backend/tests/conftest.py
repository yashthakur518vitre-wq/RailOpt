import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def sample_task():
    return {
        "task_id": "T001",
        "asset_id": "A001",
        "department": "Engineering",
        "task_type": "Track Maintenance",
        "description": "Routine track inspection",
        "created_date": date.today(),
        "due_date": date.today(),
        "estimated_duration": 2.0,
        "required_block_duration": 2.0,
        "criticality": "HIGH",
        "urgency": "MEDIUM",
        "safety_impact": "HIGH",
        "asset_impact": "MEDIUM",
        "status": "PENDING",
        "required_resources": '{"engineers": 2}',
        "preferred_time_window": "NIGHT",
        "corridor_id": "C001"
    }

@pytest.fixture  
def sample_asset():
    return {
        "asset_id": "A001",
        "asset_type": "Track",
        "department": "Engineering",
        "location": "KM 100",
        "corridor_id": "C001",
        "criticality": "HIGH",
        "installation_date": date(2010, 1, 1),
        "last_maintenance_date": date(2023, 1, 1),
        "next_due_date": date(2024, 1, 1),
        "condition_score": 85.5,
        "availability_status": "AVAILABLE",
        "failure_history": 2
    }

@pytest.fixture
def sample_corridor():
    return {
        "corridor_id": "C001",
        "name": "Delhi-Mumbai",
        "start_station": "NDLS",
        "end_station": "BCT",
        "distance_km": 1384.0,
        "route_type": "Mainline",
        "capacity": 100,
        "availability_windows": '{"00:00-04:00": true}'
    }

@pytest.fixture
def sample_train():
    return {
        "train_id": "TR001",
        "train_number": "12951",
        "train_type": "Rajdhani",
        "origin": "BCT",
        "destination": "NDLS",
        "corridor_id": "C001",
        "arrival_time": "08:30",
        "departure_time": "17:00",
        "frequency": "Daily",
        "priority": "HIGH",
        "occupancy": 95.0,
        "forecasted": False
    }

@pytest.fixture
def sample_defect():
    return {
        "defect_id": "D001",
        "asset_id": "A001",
        "department": "Engineering",
        "severity": "HIGH",
        "detected_date": date.today(),
        "description": "Rail fracture",
        "failure_probability": 0.8,
        "safety_impact": "CRITICAL",
        "operational_impact": "HIGH",
        "status": "OPEN"
    }
