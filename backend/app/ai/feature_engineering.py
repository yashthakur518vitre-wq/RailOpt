from datetime import date
from typing import Dict, List, Any

# Category maps
CRITICALITY_MAP = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
SEVERITY_MAP = {'Critical': 4, 'Major': 3, 'Minor': 2, 'Cosmetic': 1}
SAFETY_IMPACT_MAP = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
ROUTE_TYPE_MAP = {'Main': 3, 'Branch': 2, 'Suburban': 1}
URGENCY_MAP = {'Immediate': 4, 'Urgent': 3, 'Normal': 2, 'Low': 1}
TRAIN_TYPE_MAP = {'Rajdhani': 6, 'Shatabdi': 5, 'Express': 4, 'Passenger': 3, 'Goods': 2, 'Suburban': 1}

def calculate_overdue_days(due_date: date, reference_date: date = None) -> int:
    """Days past due. Negative means not yet due."""
    if not reference_date:
        reference_date = date.today()
    if isinstance(due_date, str):
        due_date = date.fromisoformat(due_date)
    if isinstance(reference_date, str):
        reference_date = date.fromisoformat(reference_date)
    return (reference_date - due_date).days

def calculate_asset_age(installation_date: date, reference_date: date = None) -> float:
    """Asset age in years."""
    if not reference_date:
        reference_date = date.today()
    if isinstance(installation_date, str):
        installation_date = date.fromisoformat(installation_date)
    if isinstance(reference_date, str):
        reference_date = date.fromisoformat(reference_date)
    return (reference_date - installation_date).days / 365.25

def calculate_failure_risk_features(condition_score: float, failure_history: int, asset_age: float, defect_severity: str, overdue_days: int) -> dict:
    """Returns dict of risk-related features."""
    return {
        'condition_score': condition_score,
        'failure_history': failure_history,
        'asset_age': asset_age,
        'defect_severity_max': encode_categorical(defect_severity, SEVERITY_MAP),
        'overdue_days': overdue_days
    }

def calculate_train_density(corridor_id: str, trains: List[Dict[str, Any]]) -> float:
    """Number of trains per day on a corridor."""
    corridor_trains = [t for t in trains if t.get('corridor_id') == corridor_id]
    return float(len(corridor_trains))

def calculate_operational_impact(train_density: float, corridor_route_type: str, block_duration: float) -> float:
    """Operational impact score 0-100."""
    route_val = encode_categorical(corridor_route_type, ROUTE_TYPE_MAP)
    impact = (train_density * 0.5) + (route_val * 10) + (block_duration * 5)
    return min(100.0, max(0.0, impact))

def encode_categorical(value: str, category_map: Dict[str, int]) -> int:
    """Encode string categories to integers."""
    if not value:
        return 0
    return category_map.get(value, 0)

def build_priority_features(task: Dict[str, Any], asset: Dict[str, Any], defects: List[Dict[str, Any]], trains: List[Dict[str, Any]], corridor: Dict[str, Any]) -> Dict[str, Any]:
    """Build complete feature vector for priority prediction."""
    asset_criticality = encode_categorical(asset.get('criticality', ''), CRITICALITY_MAP)
    
    due_date = task.get('due_date')
    if due_date:
        days_overdue = calculate_overdue_days(due_date)
    else:
        days_overdue = 0
        
    defect_severities = [encode_categorical(d.get('severity', ''), SEVERITY_MAP) for d in defects]
    defect_severity_max = max(defect_severities) if defect_severities else 0
    
    failure_probs = [d.get('failure_probability', 0.0) for d in defects]
    failure_probability_max = max(failure_probs) if failure_probs else 0.0
    
    safety_impact = encode_categorical(task.get('safety_impact', ''), SAFETY_IMPACT_MAP)
    
    train_density = calculate_train_density(corridor.get('corridor_id', ''), trains)
    operational_impact = calculate_operational_impact(train_density, corridor.get('route_type', ''), task.get('required_block_duration', 0.0))
    
    condition_score = asset.get('condition_score', 100.0)
    
    install_date = asset.get('installation_date')
    if install_date:
        asset_age = calculate_asset_age(install_date)
    else:
        asset_age = 0.0
        
    maintenance_duration = task.get('required_block_duration', 0.0)
    historical_failures = asset.get('failure_history', 0)
    
    return {
        'asset_criticality': asset_criticality,
        'days_overdue': days_overdue,
        'defect_severity_max': defect_severity_max,
        'failure_probability_max': failure_probability_max,
        'safety_impact': safety_impact,
        'operational_impact': operational_impact,
        'asset_condition': condition_score,
        'asset_age': asset_age,
        'train_density': train_density,
        'maintenance_duration': maintenance_duration,
        'historical_failures': historical_failures
    }

def build_risk_features(asset: Dict[str, Any], defects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build feature vector for risk prediction."""
    install_date = asset.get('installation_date')
    asset_age = calculate_asset_age(install_date) if install_date else 0.0
    
    condition_score = asset.get('condition_score', 100.0)
    
    defect_severities = [encode_categorical(d.get('severity', ''), SEVERITY_MAP) for d in defects]
    defect_severity_max = max(defect_severities) if defect_severities else 0
    
    failure_history = asset.get('failure_history', 0)
    
    last_maint = asset.get('last_maintenance_date')
    if last_maint:
        maintenance_gap_days = calculate_asset_age(last_maint) * 365.25
    else:
        maintenance_gap_days = asset_age * 365.25
        
    next_due = asset.get('next_due_date')
    if next_due:
        overdue_days = calculate_overdue_days(next_due)
    else:
        overdue_days = 0
        
    criticality = encode_categorical(asset.get('criticality', ''), CRITICALITY_MAP)
    
    return {
        'asset_age': asset_age,
        'condition_score': condition_score,
        'defect_severity_max': defect_severity_max,
        'failure_history': failure_history,
        'maintenance_gap_days': maintenance_gap_days,
        'overdue_days': overdue_days,
        'criticality': criticality
    }

def build_impact_features(corridor: Dict[str, Any], trains: List[Dict[str, Any]], block_duration: float, block_start_hour: int) -> Dict[str, Any]:
    """Build feature vector for train impact prediction."""
    train_density = calculate_train_density(corridor.get('corridor_id', ''), trains)
    route_type = encode_categorical(corridor.get('route_type', ''), ROUTE_TYPE_MAP)
    
    priorities = [encode_categorical(t.get('priority', ''), TRAIN_TYPE_MAP) for t in trains]
    avg_train_priority = sum(priorities) / len(priorities) if priorities else 0.0
    
    occupancies = [t.get('occupancy', 0.0) for t in trains]
    avg_occupancy = sum(occupancies) / len(occupancies) if occupancies else 0.0
    
    num_affected_trains = int(train_density * (block_duration / 24.0))
    
    return {
        'train_density': train_density,
        'route_type': route_type,
        'block_duration': block_duration,
        'block_start_hour': float(block_start_hour),
        'avg_train_priority': avg_train_priority,
        'avg_occupancy': avg_occupancy,
        'num_affected_trains': float(num_affected_trains)
    }
