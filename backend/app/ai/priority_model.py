import os
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, Any

class PriorityModel:
    def __init__(self, model_dir: str | None = None):
        self.model_dir = str(Path(model_dir or (Path(__file__).resolve().parents[2] / 'ml_models')).resolve())
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.feature_names = [
            'asset_criticality', 'days_overdue', 'defect_severity_max', 
            'failure_probability_max', 'safety_impact', 'operational_impact', 
            'asset_condition', 'asset_age', 'train_density', 
            'maintenance_duration', 'historical_failures'
        ]
        
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train model, return metrics dict with MAE, RMSE, R2"""
        self.model.fit(X, y)
        preds = self.model.predict(X)
        return {
            'MAE': float(mean_absolute_error(y, preds)),
            'RMSE': float(np.sqrt(mean_squared_error(y, preds))),
            'R2': float(r2_score(y, preds))
        }
        
    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Return {priority_score: 0-100, priority_level: str}"""
        x_input = np.array([[features.get(f, 0.0) for f in self.feature_names]])
        score = float(self.model.predict(x_input)[0])
        score = min(100.0, max(0.0, score))
        return {
            'priority_score': score,
            'priority_level': self._score_to_level(score)
        }
        
    def save(self, version: str):
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        path = os.path.join(self.model_dir, f'priority_model_v{version}.joblib')
        joblib.dump(self.model, path)
        
    def load(self, version: str = 'latest') -> bool:
        path = os.path.join(self.model_dir, f'priority_model_v{version}.joblib')
        if os.path.exists(path):
            self.model = joblib.load(path)
            return True
        return False
        
    def _score_to_level(self, score: float) -> str:
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"
