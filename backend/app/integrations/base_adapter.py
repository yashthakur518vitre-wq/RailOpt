from abc import ABC, abstractmethod
from typing import Any

class BaseRailwayAdapter(ABC):
    """Base adapter for railway system integration.
    
    Current: Synthetic/Mock/CSV data
    Future: Real railway API integration through adapter implementations.
    """
    @abstractmethod
    def fetch_assets(self) -> list[dict]: ...
    @abstractmethod
    def fetch_maintenance_tasks(self) -> list[dict]: ...
    @abstractmethod
    def fetch_defects(self) -> list[dict]: ...
    @abstractmethod
    def fetch_trains(self) -> list[dict]: ...
    @abstractmethod
    def fetch_corridors(self) -> list[dict]: ...
    @abstractmethod
    def fetch_resources(self) -> list[dict]: ...
    @abstractmethod
    def fetch_blocks(self) -> list[dict]: ...
    
    def get_adapter_info(self) -> dict:
        return {'name': self.__class__.__name__, 'type': 'mock', 'status': 'active'}
