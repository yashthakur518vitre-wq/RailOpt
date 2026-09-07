import os
import pandas as pd
from app.integrations.base_adapter import BaseRailwayAdapter

class TrainManagementSystemAdapter(BaseRailwayAdapter):
    """Mock adapter for Train Management System (TMS). Future: Real TMS API integration."""
    def __init__(self, data_dir: str = "data"):
        base_path = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        self.data_dir = os.path.abspath(base_path)

    def fetch_assets(self) -> list[dict]:
        return []

    def fetch_maintenance_tasks(self) -> list[dict]:
        return []

    def fetch_defects(self) -> list[dict]:
        return []

    def fetch_trains(self) -> list[dict]:
        csv_path = os.path.join(self.data_dir, "sample_trains.csv")
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path).to_dict(orient="records")
        return []

    def fetch_corridors(self) -> list[dict]:
        csv_path = os.path.join(self.data_dir, "sample_corridors.csv")
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path).to_dict(orient="records")
        return []

    def fetch_resources(self) -> list[dict]:
        return []

    def fetch_blocks(self) -> list[dict]:
        return []
