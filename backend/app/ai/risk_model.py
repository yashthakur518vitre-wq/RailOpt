import os
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from typing import Dict, Any

class RiskModel:
    def __init__(self, model_dir: str | None = None):
        self.model_dir = str(Path(model_dir or (Path(__file__).resolve().parents[2] / 'ml_models')).resolve())
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.feature_names = [
            'asset_age', 'condition_score', 'defect_severity_max', 
            'failure_history', 'maintenance_gap_days', 'overdue_days', 'criticality'
        ]
        
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train model, return metrics with accuracy, precision, recall, f1, roc_auc"""
        self.model.fit(X, y)
        preds = self.model.predict(X)
        probs = self.model.predict_proba(X)[:, 1] if len(np.unique(y)) > 1 else np.zeros(len(y))
        
        metrics = {
            'Accuracy': float(accuracy_score(y, preds)),
            'Precision': float(precision_score(y, preds, zero_division=0)),
            'Recall': float(recall_score(y, preds, zero_division=0)),
            'F1': float(f1_score(y, preds, zero_division=0))
        }
        try:
            metrics['ROC_AUC'] = float(roc_auc_score(y, probs))
        except ValueError:
            metrics['ROC_AUC'] = 0.5
        return metrics
        
    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Return {failure_risk: 0-1 probability, risk_percentage: 0-100}"""
        x_input = np.array([[features.get(f, 0.0) for f in self.feature_names]])
        try:
            prob = float(self.model.predict_proba(x_input)[0, 1])
        except Exception:
            prob = float(self.model.predict(x_input)[0]) if hasattr(self.model, "classes_") else 0.0
            
        return {
            'failure_risk': prob,
            'risk_percentage': prob * 100.0
        }
        
    def save(self, version: str):
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        path = os.path.join(self.model_dir, f'risk_model_v{version}.joblib')
        joblib.dump(self.model, path)
        
    def load(self, version: str = 'latest') -> bool:
        path = os.path.join(self.model_dir, f'risk_model_v{version}.joblib')
        if os.path.exists(path):
            self.model = joblib.load(path)
            return True
        return False
