from typing import Dict, List, Any
from app.ai.priority_model import PriorityModel
from app.ai.risk_model import RiskModel
from app.ai.impact_model import ImpactModel
from app.ai.feature_engineering import build_priority_features, build_risk_features, build_impact_features
from app.ai.feature_engineering import SEVERITY_MAP
from app.core.config import settings

class RailBlockPredictor:
    def __init__(self, model_dir: str | None = None):
        self.model_dir = model_dir or settings.MODEL_DIR
        self.priority_model = PriorityModel(model_dir)
        self.risk_model = RiskModel(model_dir)
        self.impact_model = ImpactModel(model_dir)
        self.initialized = False

    def initialize(self):
        """Load or train all models"""
        self.priority_model.load('1')
        self.risk_model.load('1')
        self.impact_model.load('1')
        self.initialized = True

    def predict_priority(self, task: Dict[str, Any], asset: Dict[str, Any], defects: List[Dict[str, Any]], trains: List[Dict[str, Any]], corridor: Dict[str, Any]) -> Dict[str, Any]:
        features = build_priority_features(task, asset, defects, trains, corridor)
        pred = self.priority_model.predict(features)
        
        risk_res = self.predict_risk(asset, defects)
        
        reasons = self.generate_reasons(task, asset, defects, pred['priority_score'], risk_res)
        recommendation = self.generate_recommendation(pred['priority_level'], risk_res['risk_percentage'])
        criticality_prediction = pred['priority_level'].capitalize()
        urgency_prediction = self.generate_urgency(pred['priority_score'], risk_res['risk_percentage'])
        
        return {
            'priority_score': pred['priority_score'],
            'priority_level': pred['priority_level'],
            'criticality_prediction': criticality_prediction,
            'urgency_prediction': urgency_prediction,
            'reasons': reasons,
            'recommendation': recommendation
        }

    def generate_urgency(self, priority_score: float, risk_percentage: float) -> str:
        if priority_score >= 80 or risk_percentage >= 80:
            return "High"
        elif priority_score >= 50 or risk_percentage >= 50:
            return "Medium"
        else:
            return "Low"

    def predict_risk(self, asset: Dict[str, Any], defects: List[Dict[str, Any]]) -> Dict[str, Any]:
        features = build_risk_features(asset, defects)
        return self.risk_model.predict(features)

    def predict_impact(self, corridor: Dict[str, Any], trains: List[Dict[str, Any]], block_duration: float, block_start_hour: int) -> Dict[str, Any]:
        features = build_impact_features(corridor, trains, block_duration, block_start_hour)
        return self.impact_model.predict(features)

    def generate_reasons(self, task: Dict[str, Any], asset: Dict[str, Any], defects: List[Dict[str, Any]], priority_score: float, risk_result: Dict[str, Any]) -> List[str]:
        reasons = []
        
        due_date = task.get('due_date')
        if due_date:
            from app.ai.feature_engineering import calculate_overdue_days
            days = calculate_overdue_days(due_date)
            if days > 0:
                reasons.append(f'Asset is {days} days overdue for maintenance')
                
        crit = asset.get('criticality')
        if crit:
            reasons.append(f'Asset criticality is {crit}')
            
        if defects:
            max_sev = 'Cosmetic'
            max_val = 0
            for d in defects:
                sev = d.get('severity', '')
                val = SEVERITY_MAP.get(sev, 0)
                if val > max_val:
                    max_val = val
                    max_sev = sev
            reasons.append(f'Defect severity is {max_sev}')
            
        cond = asset.get('condition_score')
        if cond is not None:
            cond_str = "poor" if cond < 50 else ("fair" if cond < 80 else "good")
            reasons.append(f'Asset condition score is {cond}/100 ({cond_str})')
            
        fails = asset.get('failure_history', 0)
        if fails > 0:
            reasons.append(f'Previous failure history: {fails} incidents')
            
        risk_pct = risk_result.get('risk_percentage', 0.0)
        if risk_pct > 50.0:
            reasons.append(f'Elevated failure risk: {risk_pct:.1f}%')
            
        if not reasons:
            reasons.append('Routine maintenance priority')
            
        return reasons

    def generate_recommendation(self, priority_level: str, risk_percentage: float) -> str:
        if priority_level == 'CRITICAL' or risk_percentage >= 80:
            return "Immediate action required. Schedule block within 24-48 hours."
        elif priority_level == 'HIGH' or risk_percentage >= 60:
            return "High priority. Schedule block within the next 7 days."
        elif priority_level == 'MEDIUM':
            return "Standard priority. Schedule within normal maintenance window."
        else:
            return "Low priority. Can be deferred or combined with other blocks."
