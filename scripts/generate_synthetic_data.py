import pandas as pd
import numpy as np
import random
import json
import os
from datetime import datetime, timedelta

def generate_all_data():
    random.seed(42)
    np.random.seed(42)
    
    current_date = datetime.strptime("2026-09-01", "%Y-%m-%d").date()

    # 1. Corridors (12)
    corridors_data = [
        {"corridor_id": "COR-001", "name": "Delhi-Mumbai Rajdhani", "start_station": "New Delhi", "end_station": "Mumbai Central", "distance_km": 1384.0, "route_type": "Main", "capacity": 8, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 0, "end_hour": 5}, {"day": "0-6", "start_hour": 23, "end_hour": 24}])},
        {"corridor_id": "COR-002", "name": "Delhi-Kolkata", "start_station": "New Delhi", "end_station": "Howrah", "distance_km": 1530.0, "route_type": "Main", "capacity": 7, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 0, "end_hour": 5}, {"day": "0-6", "start_hour": 23, "end_hour": 24}])},
        {"corridor_id": "COR-003", "name": "Delhi-Chennai", "start_station": "New Delhi", "end_station": "Chennai Central", "distance_km": 2180.0, "route_type": "Main", "capacity": 6, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 0, "end_hour": 5}, {"day": "0-6", "start_hour": 23, "end_hour": 24}])},
        {"corridor_id": "COR-004", "name": "Mumbai-Chennai", "start_station": "Mumbai CST", "end_station": "Chennai Central", "distance_km": 1280.0, "route_type": "Main", "capacity": 6, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 0, "end_hour": 5}, {"day": "0-6", "start_hour": 23, "end_hour": 24}])},
        {"corridor_id": "COR-005", "name": "Kolkata-Chennai", "start_station": "Howrah", "end_station": "Chennai Central", "distance_km": 1660.0, "route_type": "Main", "capacity": 5, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 0, "end_hour": 5}, {"day": "0-6", "start_hour": 23, "end_hour": 24}])},
        {"corridor_id": "COR-006", "name": "Delhi-Jaipur", "start_station": "New Delhi", "end_station": "Jaipur", "distance_km": 308.0, "route_type": "Branch", "capacity": 5, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 1, "end_hour": 6}])},
        {"corridor_id": "COR-007", "name": "Mumbai-Pune", "start_station": "Mumbai CST", "end_station": "Pune", "distance_km": 192.0, "route_type": "Branch", "capacity": 6, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 1, "end_hour": 6}])},
        {"corridor_id": "COR-008", "name": "Chennai-Bangalore", "start_station": "Chennai Central", "end_station": "Bangalore", "distance_km": 362.0, "route_type": "Branch", "capacity": 5, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 1, "end_hour": 6}])},
        {"corridor_id": "COR-009", "name": "Mumbai Suburban West", "start_station": "Churchgate", "end_station": "Virar", "distance_km": 60.0, "route_type": "Suburban", "capacity": 10, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 1, "end_hour": 4}])},
        {"corridor_id": "COR-010", "name": "Mumbai Suburban Central", "start_station": "CST", "end_station": "Kasara", "distance_km": 120.0, "route_type": "Suburban", "capacity": 10, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 1, "end_hour": 4}])},
        {"corridor_id": "COR-011", "name": "Delhi-Lucknow", "start_station": "New Delhi", "end_station": "Lucknow", "distance_km": 524.0, "route_type": "Main", "capacity": 6, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 0, "end_hour": 5}, {"day": "0-6", "start_hour": 23, "end_hour": 24}])},
        {"corridor_id": "COR-012", "name": "Kolkata Suburban", "start_station": "Sealdah", "end_station": "Ranaghat", "distance_km": 80.0, "route_type": "Suburban", "capacity": 8, "availability_windows": json.dumps([{"day": "0-6", "start_hour": 1, "end_hour": 4}])},
    ]
    df_corridors = pd.DataFrame(corridors_data)
    corridor_ids = df_corridors['corridor_id'].tolist()
    
    # 2. Assets (120)
    assets = []
    asset_types = ["Track", "Bridge", "Signal", "Switch", "OHE", "Station"]
    type_weights = [0.4, 0.1, 0.2, 0.15, 0.1, 0.05]
    departments = ["Engineering", "S&T", "Traction", "Operations"]
    dept_weights = [0.5, 0.25, 0.2, 0.05]
    
    for i in range(1, 121):
        atype = np.random.choice(asset_types, p=type_weights)
        dept = np.random.choice(departments, p=dept_weights)
        cor = np.random.choice(corridor_ids)
        c_score = np.random.choice([np.random.uniform(10, 30), np.random.uniform(40, 90), np.random.uniform(90, 100)], p=[0.15, 0.7, 0.15])
        fail_hist = int(max(0, (100 - c_score) / 10 + np.random.normal(0, 1)))
        fail_hist = min(8, fail_hist)
        inst_year = np.random.randint(1990, 2024)
        if c_score < 40 and inst_year > 2010:
            inst_year = np.random.randint(1990, 2005)
        
        inst_date = datetime(inst_year, np.random.randint(1, 13), np.random.randint(1, 28)).date()
        
        last_m_date = current_date - timedelta(days=np.random.randint(10, 300))
        next_d_date = last_m_date + timedelta(days=np.random.randint(90, 365))
        
        if c_score < 40:
            next_d_date = current_date - timedelta(days=np.random.randint(1, 60))
            
        crit = np.random.choice(["Critical", "High", "Medium", "Low"], p=[0.15, 0.25, 0.4, 0.2])
        if "Main" in df_corridors[df_corridors['corridor_id'] == cor]['route_type'].values[0]:
            crit = np.random.choice(["Critical", "High"], p=[0.4, 0.6])

        assets.append({
            "asset_id": f"AST-{i:03d}",
            "asset_type": atype,
            "department": dept,
            "location": f"Loc-{(np.random.randint(1, 1000))}km",
            "corridor_id": cor,
            "criticality": crit,
            "installation_date": inst_date,
            "last_maintenance_date": last_m_date,
            "next_due_date": next_d_date,
            "condition_score": c_score,
            "availability_status": "Available" if c_score > 30 else "Requires Maintenance",
            "failure_history": fail_hist
        })
    df_assets = pd.DataFrame(assets)

    # 3. Defects (120)
    defects = []
    asset_ids = df_assets['asset_id'].tolist()
    for i in range(1, 121):
        ast_id = np.random.choice(asset_ids)
        sev = np.random.choice(["Critical", "Major", "Minor", "Cosmetic"], p=[0.15, 0.3, 0.4, 0.15])
        fail_prob = {
            "Critical": np.random.uniform(0.6, 0.9),
            "Major": np.random.uniform(0.3, 0.6),
            "Minor": np.random.uniform(0.1, 0.3),
            "Cosmetic": np.random.uniform(0.01, 0.1)
        }[sev]
        
        defects.append({
            "defect_id": f"DEF-{i:03d}",
            "asset_id": ast_id,
            "department": df_assets[df_assets['asset_id'] == ast_id]['department'].values[0],
            "severity": sev,
            "detected_date": current_date - timedelta(days=np.random.randint(1, 30)),
            "description": f"{sev} defect on {ast_id}",
            "failure_probability": fail_prob,
            "safety_impact": "High" if sev in ["Critical", "Major"] else "Low",
            "operational_impact": "High" if sev == "Critical" else "Medium",
            "status": np.random.choice(["Open", "Under_Investigation", "Repair_Scheduled", "Resolved"], p=[0.5, 0.2, 0.2, 0.1])
        })
    df_defects = pd.DataFrame(defects)

    # 4. Resources (30)
    resources = []
    caps = ["Track_Gang", "Track_Machine", "Welding_Unit", "Signal_Team", "Telecom_Team", "OHE_Team", "Bridge_Inspector", "Rail_Testing", "Point_Machine_Team", "SCADA_Team"]
    depts = ["Engineering", "S&T", "Traction"]
    for i in range(1, 31):
        resources.append({
            "resource_id": f"RES-{i:03d}",
            "name": f"Resource-{i}",
            "department": np.random.choice(depts),
            "capability": np.random.choice(caps),
            "availability": np.random.choice(["Available", "Busy", "Off_Duty"], p=[0.7, 0.2, 0.1]),
            "quantity": np.random.randint(1, 6)
        })
    df_resources = pd.DataFrame(resources)
    
    # 5. Maintenance Tasks (250)
    tasks = []
    t_types = ["Preventive", "Corrective", "Emergency", "Inspection"]
    for i in range(1, 251):
        ast = df_assets.sample(1).iloc[0]
        ttype = np.random.choice(t_types, p=[0.4, 0.3, 0.1, 0.2])
        duration = np.random.uniform(0.5, 4.0)
        req_dur = duration * np.random.uniform(1.1, 1.5)
        
        due = current_date + timedelta(days=np.random.randint(-10, 30))
        if i <= 30: 
            due = current_date - timedelta(days=np.random.randint(1, 15))
            
        urgency = np.random.choice(["Critical", "High", "Medium", "Low"])
        if i > 30 and i <= 45:
            urgency = "Critical"
            
        req_res = ",".join(np.random.choice(caps, size=np.random.randint(1, 3), replace=False))
        if i > 45 and i <= 55:
            req_res = "Welding_Unit"
            
        pref_win = np.random.choice(["Night", "Early_Morning", "Morning", "Afternoon", "Any"])
        cor = ast['corridor_id']
        if i > 55 and i <= 63:
            pref_win = "Night"
            cor = "COR-001"
            
        dep = None
        if i > 63 and i <= 68:
            dep = f"TSK-{(i-1):03d}" if i > 64 else None
            
        tasks.append({
            "task_id": f"TSK-{i:03d}",
            "asset_id": ast['asset_id'],
            "department": ast['department'],
            "task_type": ttype,
            "description": f"{ttype} maintenance on {ast['asset_type']}",
            "created_date": current_date - timedelta(days=np.random.randint(1, 60)),
            "due_date": due,
            "estimated_duration": duration,
            "required_block_duration": req_dur,
            "criticality": ast['criticality'],
            "urgency": urgency,
            "safety_impact": "High" if ast['criticality'] == "Critical" else "Medium",
            "asset_impact": "High",
            "status": "OVERDUE" if due < current_date else np.random.choice(["PENDING", "SCHEDULED", "IN_PROGRESS", "COMPLETED"], p=[0.7, 0.15, 0.05, 0.1]),
            "required_resources": req_res,
            "preferred_time_window": pref_win,
            "corridor_id": cor,
            "dependency_task_id": dep,
            "ai_priority_score": None,
            "ai_priority_level": None,
            "ai_failure_risk": None,
            "ai_risk_percentage": None,
            "ai_train_impact_score": None,
            "ai_reasons": None,
            "ai_model_version": None
        })
    df_tasks = pd.DataFrame(tasks)

    # 6. Trains (55)
    trains = []
    train_types = ["Rajdhani", "Shatabdi", "Express", "Passenger", "Goods", "Suburban"]
    t_weights = [5/55, 5/55, 15/55, 10/55, 10/55, 10/55]
    priorities = {"Rajdhani": "Critical", "Shatabdi": "Critical", "Express": "High", "Passenger": "Medium", "Suburban": "Medium", "Goods": "Low"}
    
    for i in range(1, 56):
        ttype = np.random.choice(train_types, p=t_weights)
        hr = np.random.randint(0, 24)
        if np.random.random() < 0.6: 
            hr = np.random.choice([6, 7, 8, 9, 10, 16, 17, 18, 19, 20, 21, 22])
        arr = f"{hr:02d}:{np.random.randint(0,60):02d}"
        dep = f"{(hr + np.random.randint(1,3)) % 24:02d}:{np.random.randint(0,60):02d}"
        
        trains.append({
            "train_id": f"TRN-{i:03d}",
            "train_number": str(np.random.randint(10000, 99999)),
            "train_type": ttype,
            "origin": "Station A",
            "destination": "Station B",
            "corridor_id": np.random.choice(corridor_ids),
            "arrival_time": arr,
            "departure_time": dep,
            "frequency": "Daily",
            "priority": priorities[ttype],
            "occupancy": np.random.uniform(40, 100),
            "forecasted": bool(ttype == "Goods" and np.random.random() < 0.5)
        })
    df_trains = pd.DataFrame(trains)

    # 7. Blocks (20)
    blocks = []
    for i in range(1, 21):
        st = datetime.combine(current_date + timedelta(days=np.random.randint(0, 5)), datetime.min.time()) + timedelta(hours=np.random.randint(0, 20))
        et = st + timedelta(hours=np.random.uniform(1, 4))
        blocks.append({
            "block_id": f"BLK-{i:03d}",
            "corridor_id": np.random.choice(corridor_ids),
            "start_time": st,
            "end_time": et,
            "duration": (et - st).total_seconds() / 3600,
            "status": "APPROVED",
            "source": np.random.choice(["Manual", "Historical"]),
            "department": np.random.choice(depts),
            "reason": "Scheduled Maintenance",
            "plan_id": None
        })
    df_blocks = pd.DataFrame(blocks)

    return {
        "corridors": df_corridors,
        "assets": df_assets,
        "defects": df_defects,
        "resources": df_resources,
        "tasks": df_tasks,
        "trains": df_trains,
        "blocks": df_blocks
    }

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "data")
    os.makedirs(data_dir, exist_ok=True)
    data = generate_all_data()
    data["assets"].to_csv(os.path.join(data_dir, "sample_assets.csv"), index=False)
    data["tasks"].to_csv(os.path.join(data_dir, "sample_tasks.csv"), index=False)
    data["defects"].to_csv(os.path.join(data_dir, "sample_defects.csv"), index=False)
    data["trains"].to_csv(os.path.join(data_dir, "sample_trains.csv"), index=False)
    data["corridors"].to_csv(os.path.join(data_dir, "sample_corridors.csv"), index=False)
    data["blocks"].to_csv(os.path.join(data_dir, "sample_blocks.csv"), index=False)
    data["resources"].to_csv(os.path.join(data_dir, "sample_resources.csv"), index=False)
    print("Generated synthetic data in backend/data/")
