import pytest
from app.services.planning_service import PlanningService
from app.models import MaintenanceTask, Asset, Corridor, Defect, Train, Resource
from sqlalchemy.orm import Session

def test_full_planning_pipeline(db_session: Session):
    # This assumes db_session has been seeded or we can just run planning on whatever is there.
    # Because we're in-memory, db_session is empty initially unless conftest seeds it.
    
    # We will seed some basic data manually here to ensure it runs E2E.
    import datetime
    
    corridor = Corridor(corridor_id='C1', name='C1', start_station='A', end_station='B', distance_km=10, route_type='Main', capacity=10, availability_windows='[{"day": "0-6", "start_hour": 0, "end_hour": 5}]')
    asset = Asset(asset_id='A1', asset_type='Track', department='TRACK', location='Loc1', corridor_id='C1', criticality='HIGH', installation_date=datetime.date(2020, 1, 1), last_maintenance_date=datetime.date(2023, 1, 1), next_due_date=datetime.date(2024, 1, 1), condition_score=40.0, availability_status='Available')
    task = MaintenanceTask(task_id='T1', asset_id='A1', department='TRACK', task_type='PREVENTIVE', description='Test', created_date=datetime.datetime(2024, 1, 1), due_date=datetime.datetime(2024, 1, 1), estimated_duration=2.0, required_block_duration=2.0, criticality='HIGH', urgency='Normal', safety_impact='Medium', asset_impact='High', status='PENDING', required_resources='R1', preferred_time_window='Night', corridor_id='C1')
    resource = Resource(resource_id='R1', name='R1', department='TRACK', capability='General', quantity=5, availability='Available')
    
    db_session.add_all([corridor, asset, task, resource])
    db_session.commit()
    
    plan_result = PlanningService.generate_plan(db_session, 'weekly')
    
    assert plan_result is not None
    assert 'plan' in plan_result
    assert 'blocks' in plan_result
    assert 'comparison' in plan_result
    
    assert len(plan_result['scheduled_tasks']) + len(plan_result['unscheduled_tasks']) == 1
