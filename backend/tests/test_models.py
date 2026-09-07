import pytest
from app.models.asset import Asset
from app.models.maintenance_task import MaintenanceTask
from app.models.corridor import Corridor
from app.models.train import Train
from app.models.defect import Defect
from app.models.block import Block
from app.models.resource import Resource
from app.models.plan import Plan

def test_asset_model(db_session, sample_asset):
    asset = Asset(**sample_asset)
    db_session.add(asset)
    db_session.commit()
    
    saved_asset = db_session.query(Asset).filter_by(asset_id="A001").first()
    assert saved_asset is not None
    assert saved_asset.asset_type == "Track"
    assert saved_asset.condition_score == 85.5

def test_maintenance_task_model(db_session, sample_task):
    task = MaintenanceTask(**sample_task)
    db_session.add(task)
    db_session.commit()
    
    saved_task = db_session.query(MaintenanceTask).filter_by(task_id="T001").first()
    assert saved_task is not None
    assert saved_task.department == "Engineering"
    assert saved_task.estimated_duration == 2.0

def test_corridor_model(db_session, sample_corridor):
    corridor = Corridor(**sample_corridor)
    db_session.add(corridor)
    db_session.commit()
    
    saved_corridor = db_session.query(Corridor).filter_by(corridor_id="C001").first()
    assert saved_corridor is not None
    assert saved_corridor.distance_km == 1384.0

def test_train_model(db_session, sample_train):
    train = Train(**sample_train)
    db_session.add(train)
    db_session.commit()
    
    saved_train = db_session.query(Train).filter_by(train_id="TR001").first()
    assert saved_train is not None
    assert saved_train.occupancy == 95.0

def test_defect_model(db_session, sample_defect):
    defect = Defect(**sample_defect)
    db_session.add(defect)
    db_session.commit()
    
    saved_defect = db_session.query(Defect).filter_by(defect_id="D001").first()
    assert saved_defect is not None
    assert saved_defect.failure_probability == 0.8
