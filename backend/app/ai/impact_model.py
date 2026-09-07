import os
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, Any

class ImpactModel:
    def __init__(self, model_dir: str | None = None):
        self.model_dir = str(Path(model_dir or (Path(__file__).resolve().parents[2] / 'ml_models')).resolve())
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.feature_names = [
            'train_density', 'route_type', 'block_duration', 
            'block_start_hour', 'avg_train_priority', 'avg_occupancy', 
            'num_affected_trains'
        ]
        
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        self.model.fit(X, y)
        preds = self.model.predict(X)
        return {
            'MAE': float(mean_absolute_error(y, preds)),
            'RMSE': float(np.sqrt(mean_squared_error(y, preds))),
            'R2': float(r2_score(y, preds))
        }
        
    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        x_input = np.array([[features.get(f, 0.0) for f in self.feature_names]])
        score = float(self.model.predict(x_input)[0])
        score = min(100.0, max(0.0, score))
        return {
            'train_impact_score': score
        }
        
    def save(self, version: str):
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        path = os.path.join(self.model_dir, f'impact_model_v{version}.joblib')
        joblib.dump(self.model, path)
        
    def load(self, version: str = 'latest') -> bool:
        path = os.path.join(self.model_dir, f'impact_model_v{version}.joblib')
        if os.path.exists(path):
            self.model = joblib.load(path)
            return True
        return False
