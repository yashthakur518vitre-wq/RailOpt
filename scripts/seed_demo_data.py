import sys, os
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.database.database import engine, SessionLocal, init_db
from app.database.base import Base
from app.models import Asset, MaintenanceTask, Defect, Corridor, Train, Block, Resource
from generate_synthetic_data import generate_all_data

def clear_db(session: Session):
    for model in [Asset, MaintenanceTask, Defect, Corridor, Train, Block, Resource]:
        session.query(model).delete()
    session.commit()

def safe_date(d):
    if pd.isna(d):
        return None
    if isinstance(d, str):
        return datetime.strptime(d, "%Y-%m-%d").date()
    return d

def safe_datetime(d):
    if pd.isna(d):
        return None
    if isinstance(d, str):
        return datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
    return d
    
def seed_data():
    print("Generating synthetic data...")
    data = generate_all_data()
    
    # Save CSVs
    data_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "data")
    os.makedirs(data_dir, exist_ok=True)
    data["assets"].to_csv(os.path.join(data_dir, "sample_assets.csv"), index=False)
    data["tasks"].to_csv(os.path.join(data_dir, "sample_tasks.csv"), index=False)
    data["defects"].to_csv(os.path.join(data_dir, "sample_defects.csv"), index=False)
    data["trains"].to_csv(os.path.join(data_dir, "sample_trains.csv"), index=False)
    data["corridors"].to_csv(os.path.join(data_dir, "sample_corridors.csv"), index=False)
    data["blocks"].to_csv(os.path.join(data_dir, "sample_blocks.csv"), index=False)
    data["resources"].to_csv(os.path.join(data_dir, "sample_resources.csv"), index=False)

    print("Connecting to DB and initializing...")
    init_db()
    
    session = SessionLocal()
    try:
        print("Clearing old data...")
        clear_db(session)
        
        print("Inserting Corridors...")
        for _, row in data["corridors"].iterrows():
            session.add(Corridor(**row.to_dict()))
            
        print("Inserting Assets...")
        for _, row in data["assets"].iterrows():
            d = row.to_dict()
            d['installation_date'] = safe_date(d.get('installation_date'))
            d['last_maintenance_date'] = safe_date(d.get('last_maintenance_date'))
            d['next_due_date'] = safe_date(d.get('next_due_date'))
            session.add(Asset(**d))
            
        print("Inserting Defects...")
        for _, row in data["defects"].iterrows():
            d = row.to_dict()
            d['detected_date'] = safe_date(d.get('detected_date'))
            session.add(Defect(**d))

        print("Inserting Resources...")
        for _, row in data["resources"].iterrows():
            session.add(Resource(**row.to_dict()))
            
        print("Inserting Maintenance Tasks...")
        for _, row in data["tasks"].iterrows():
            d = row.to_dict()
            d['created_date'] = safe_date(d.get('created_date'))
            d['due_date'] = safe_date(d.get('due_date'))
            d['dependency_task_id'] = d['dependency_task_id'] if pd.notna(d['dependency_task_id']) else None
            session.add(MaintenanceTask(**d))
            
        print("Inserting Trains...")
        for _, row in data["trains"].iterrows():
            session.add(Train(**row.to_dict()))
            
        print("Inserting Blocks...")
        for _, row in data["blocks"].iterrows():
            d = row.to_dict()
            d['start_time'] = safe_datetime(d.get('start_time'))
            d['end_time'] = safe_datetime(d.get('end_time'))
            d['plan_id'] = d['plan_id'] if pd.notna(d['plan_id']) else None
            session.add(Block(**d))
            
        session.commit()
        print("Done successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error seeding data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()
