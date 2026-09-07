import os
import pandas as pd
from app.integrations.base_adapter import BaseRailwayAdapter

class SectionMaintenanceManagementAdapter(BaseRailwayAdapter):
    """Mock adapter for Section Maintenance Management System (SMMS)."""
    def __init__(self):
        base_path = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        self.data_dir = os.path.abspath(base_path)

    def fetch_assets(self) -> list[dict]:
        csv_path = os.path.join(self.data_dir, "sample_assets.csv")
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path).to_dict(orient="records")
        return []

    def fetch_maintenance_tasks(self) -> list[dict]:
        csv_path = os.path.join(self.data_dir, "sample_tasks.csv")
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path).to_dict(orient="records")
        return []

    def fetch_defects(self) -> list[dict]:
        return []

    def fetch_trains(self) -> list[dict]:
        return []

    def fetch_corridors(self) -> list[dict]:
        return []

    def fetch_resources(self) -> list[dict]:
        return []

    def fetch_blocks(self) -> list[dict]:
        return []
