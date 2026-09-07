import os
from pathlib import Path
import json
import numpy as np
from datetime import date
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from app.ai.priority_model import PriorityModel
from app.ai.risk_model import RiskModel
from app.ai.impact_model import ImpactModel

def generate_synthetic_data(num_samples: int = 500):
    np.random.seed(42)
    
    # Generate Priority features
    X_priority = np.zeros((num_samples, 11))
    X_priority[:, 0] = np.random.randint(1, 5, num_samples) # criticality
    X_priority[:, 1] = np.random.randint(-30, 365, num_samples) # days overdue
    X_priority[:, 2] = np.random.randint(0, 5, num_samples) # defect severity
    X_priority[:, 3] = np.random.uniform(0.0, 1.0, num_samples) # fail prob max
    X_priority[:, 4] = np.random.randint(1, 5, num_samples) # safety impact
    X_priority[:, 5] = np.random.uniform(0.0, 100.0, num_samples) # op impact
    X_priority[:, 6] = np.random.uniform(20.0, 100.0, num_samples) # condition
    X_priority[:, 7] = np.random.uniform(0.5, 40.0, num_samples) # age
    X_priority[:, 8] = np.random.uniform(10, 150, num_samples) # train density
    X_priority[:, 9] = np.random.uniform(1.0, 12.0, num_samples) # maintenance duration
    X_priority[:, 10] = np.random.randint(0, 10, num_samples) # failures
    
    # create priority target
    crit_norm = X_priority[:, 0] / 4.0
    over_norm = np.clip(X_priority[:, 1] / 365.0, 0, 1)
    def_norm = X_priority[:, 2] / 4.0
    cond_norm = (100 - X_priority[:, 6]) / 100.0
    fail_risk_norm = X_priority[:, 3]
    dens_norm = X_priority[:, 8] / 150.0
    dur_norm = X_priority[:, 9] / 12.0
    
    y_priority = (
        0.25 * crit_norm +
        0.20 * over_norm +
        0.15 * def_norm +
        0.15 * cond_norm +
        0.10 * fail_risk_norm +
        0.10 * dens_norm +
        0.05 * dur_norm
    ) * 100 + np.random.normal(0, 5, num_samples)
    y_priority = np.clip(y_priority, 0, 100)
    
    # Generate Risk features
    X_risk = np.zeros((num_samples, 7))
    X_risk[:, 0] = X_priority[:, 7] # age
    X_risk[:, 1] = X_priority[:, 6] # condition
    X_risk[:, 2] = X_priority[:, 2] # def max
    X_risk[:, 3] = X_priority[:, 10] # failures
    X_risk[:, 4] = np.random.uniform(30, 700, num_samples) # gap
    X_risk[:, 5] = X_priority[:, 1] # overdue
    X_risk[:, 6] = X_priority[:, 0] # crit
    
    # Risk target
    risk_prob = (
        0.3 * (X_risk[:, 0] / 40.0) +
        0.3 * ((100 - X_risk[:, 1]) / 100.0) +
        0.2 * (X_risk[:, 3] / 10.0) +
        0.2 * (X_risk[:, 2] / 4.0)
    ) + np.random.normal(0, 0.1, num_samples)
    risk_prob = np.clip(risk_prob, 0, 1)
    y_risk = (risk_prob > 0.5).astype(int)
    
    # Generate Impact features
    X_impact = np.zeros((num_samples, 7))
    X_impact[:, 0] = X_priority[:, 8] # density
    X_impact[:, 1] = np.random.randint(1, 4, num_samples) # route
    X_impact[:, 2] = X_priority[:, 9] # block dur
    X_impact[:, 3] = np.random.randint(0, 24, num_samples) # start hr
    X_impact[:, 4] = np.random.uniform(1, 6, num_samples) # avg prio
    X_impact[:, 5] = np.random.uniform(30, 100, num_samples) # avg occ
    X_impact[:, 6] = (X_impact[:, 0] * (X_impact[:, 2] / 24.0)).astype(int) # affected
    
    y_impact = (
        0.4 * (X_impact[:, 0] / 150.0) +
        0.2 * (X_impact[:, 1] / 3.0) +
        0.2 * (X_impact[:, 2] / 12.0) +
        0.2 * (X_impact[:, 5] / 100.0)
    ) * 100 + np.random.normal(0, 5, num_samples)
    
    # Peak hours impact
    peak_mask = ((X_impact[:, 3] >= 7) & (X_impact[:, 3] <= 10)) | ((X_impact[:, 3] >= 16) & (X_impact[:, 3] <= 20))
    y_impact[peak_mask] += 15
    y_impact = np.clip(y_impact, 0, 100)
    
    return (X_priority, y_priority), (X_risk, y_risk), (X_impact, y_impact)

def train_models(
    model_dir: str | None = None,
    version: str = '1',
    num_samples: int = 500,
    training_data: dict = None
) -> dict:
    """
    Train Priority, Risk, and Impact models, evaluate test metrics,
    save model artifacts (.joblib) to model_dir, and update metadata.json.
    
    Returns the metadata dictionary containing model statuses and test metrics.
    """
    model_dir = model_dir or str((Path(__file__).resolve().parents[3] / 'ml_models').resolve())
    if not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)
        
    if training_data and 'priority' in training_data and 'risk' in training_data and 'impact' in training_data:
        (X_p, y_p) = training_data['priority']
        (X_r, y_r) = training_data['risk']
        (X_i, y_i) = training_data['impact']
    else:
        samples = training_data.get('num_samples', num_samples) if isinstance(training_data, dict) else num_samples
        (X_p, y_p), (X_r, y_r), (X_i, y_i) = generate_synthetic_data(samples)
    
    X_p_train, X_p_test, y_p_train, y_p_test = train_test_split(X_p, y_p, test_size=0.2, random_state=42)
    X_r_train, X_r_test, y_r_train, y_r_test = train_test_split(X_r, y_r, test_size=0.2, random_state=42)
    X_i_train, X_i_test, y_i_train, y_i_test = train_test_split(X_i, y_i, test_size=0.2, random_state=42)
    
    # 1. Priority Model
    priority_model = PriorityModel(model_dir)
    priority_model.train(X_p_train, y_p_train)
    p_preds = priority_model.model.predict(X_p_test)
    test_p_metrics = {
        'MAE': float(mean_absolute_error(y_p_test, p_preds)),
        'RMSE': float(np.sqrt(mean_squared_error(y_p_test, p_preds))),
        'R2': float(r2_score(y_p_test, p_preds))
    }
    
    # 2. Risk Model
    risk_model = RiskModel(model_dir)
    risk_model.train(X_r_train, y_r_train)
    r_preds = risk_model.model.predict(X_r_test)
    r_probs = risk_model.model.predict_proba(X_r_test)[:, 1] if len(np.unique(y_r_train)) > 1 else np.zeros(len(y_r_test))
    test_r_metrics = {
        'Accuracy': float(accuracy_score(y_r_test, r_preds)),
        'Precision': float(precision_score(y_r_test, r_preds, zero_division=0)),
        'Recall': float(recall_score(y_r_test, r_preds, zero_division=0)),
        'F1': float(f1_score(y_r_test, r_preds, zero_division=0)),
        'ROC_AUC': float(roc_auc_score(y_r_test, r_probs)) if len(np.unique(y_r_test)) > 1 else 0.5
    }
    
    # 3. Impact Model
    impact_model = ImpactModel(model_dir)
    impact_model.train(X_i_train, y_i_train)
    i_preds = impact_model.model.predict(X_i_test)
    test_i_metrics = {
        'MAE': float(mean_absolute_error(y_i_test, i_preds)),
        'RMSE': float(np.sqrt(mean_squared_error(y_i_test, i_preds))),
        'R2': float(r2_score(y_i_test, i_preds))
    }
    
    # Save model artifacts
    priority_model.save(version)
    risk_model.save(version)
    impact_model.save(version)
    
    metadata = {
        'version': version,
        'priority_model': {
            'loaded': True,
            'version': version,
            'metrics': test_p_metrics
        },
        'risk_model': {
            'loaded': True,
            'version': version,
            'metrics': test_r_metrics
        },
        'impact_model': {
            'loaded': True,
            'version': version,
            'metrics': test_i_metrics
        }
    }
    
    with open(os.path.join(model_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
        
    return metadata

def main():
    print("=== RailBlock AI Model Training ===")
    model_dir = str((Path(__file__).resolve().parents[3] / 'ml_models').resolve())
    print("[TRAIN] Training all models...")
    metadata = train_models(model_dir=model_dir, version='1', num_samples=500)
    
    p_m = metadata['priority_model']['metrics']
    r_m = metadata['risk_model']['metrics']
    i_m = metadata['impact_model']['metrics']
    
    print(f"[METRICS] Priority Model - MAE: {p_m['MAE']:.2f}, RMSE: {p_m['RMSE']:.2f}, R²: {p_m['R2']:.2f}")
    print(f"[METRICS] Risk Model - Accuracy: {r_m['Accuracy']:.2f}, Precision: {r_m['Precision']:.2f}, Recall: {r_m['Recall']:.2f}, F1: {r_m['F1']:.2f}, ROC-AUC: {r_m['ROC_AUC']:.2f}")
    print(f"[METRICS] Impact Model - MAE: {i_m['MAE']:.2f}, RMSE: {i_m['RMSE']:.2f}, R²: {i_m['R2']:.2f}")
    print(f"[TRAIN] All models saved to {model_dir}/")
    print("\nNOTE: These are synthetic-demo models trained on generated data.")
    print("They are NOT claims about real railway failure prediction accuracy.")

if __name__ == '__main__':
    main()
