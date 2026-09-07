import os
import json
import tempfile
import pytest
from app.ai.model_manager import ModelManager


def test_model_manager_status_with_existing_models():
    # Test using backend/ml_models
    manager = ModelManager(model_dir="./ml_models")
    status = manager.get_model_status()
    assert "priority_model" in status
    assert "risk_model" in status
    assert "impact_model" in status
    # Trained .joblib artifacts ship in backend/ml_models, so they should load successfully
    assert status["priority_model"]["loaded"] is True
    assert status["risk_model"]["loaded"] is True
    assert status["impact_model"]["loaded"] is True
    assert manager.models_available() is True


def test_model_manager_status_missing_files(tmp_path):
    # Empty temp directory has no model files
    manager = ModelManager(model_dir=str(tmp_path))
    status = manager.get_model_status()
    assert status["priority_model"]["loaded"] is False
    assert status["risk_model"]["loaded"] is False
    assert status["impact_model"]["loaded"] is False
    assert manager.models_available() is False


def test_model_manager_metadata_present_but_files_missing(tmp_path):
    # Create metadata.json claiming loaded=True, but no .joblib files
    metadata = {
        "version": "1",
        "priority_model": {"loaded": True, "version": "1", "metrics": {"MAE": 5.0}},
        "risk_model": {"loaded": True, "version": "1", "metrics": {"Accuracy": 0.8}},
        "impact_model": {"loaded": True, "version": "1", "metrics": {"MAE": 4.0}}
    }
    with open(tmp_path / "metadata.json", "w") as f:
        json.dump(metadata, f)

    manager = ModelManager(model_dir=str(tmp_path))
    status = manager.get_model_status()
    # Should detect that files do NOT actually exist
    assert status["priority_model"]["loaded"] is False
    assert status["risk_model"]["loaded"] is False
    assert status["impact_model"]["loaded"] is False
    assert manager.models_available() is False


def test_model_manager_train_all_models(tmp_path):
    model_dir = str(tmp_path / "models")
    manager = ModelManager(model_dir=model_dir)

    metrics = manager.train_all_models({"num_samples": 50})
    assert "priority_model" in metrics
    assert "risk_model" in metrics
    assert "impact_model" in metrics
    assert "MAE" in metrics["priority_model"]["metrics"]
    assert "Accuracy" in metrics["risk_model"]["metrics"]
    assert "MAE" in metrics["impact_model"]["metrics"]

    # Verify model files exist on disk
    assert os.path.exists(os.path.join(model_dir, "priority_model_v1.joblib"))
    assert os.path.exists(os.path.join(model_dir, "risk_model_v1.joblib"))
    assert os.path.join(model_dir, "impact_model_v1.joblib")
    assert os.path.exists(os.path.join(model_dir, "metadata.json"))

    # Verify status and availability
    assert manager.models_available() is True
    status = manager.get_model_status()
    assert status["priority_model"]["loaded"] is True
    assert status["risk_model"]["loaded"] is True
    assert status["impact_model"]["loaded"] is True
