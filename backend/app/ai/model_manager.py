import os
import json
import logging
from typing import Dict, Any, Optional
from app.ai.predictor import RailBlockPredictor
from app.ai.training.train_models import train_models, generate_synthetic_data
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    REQUIRED_MODELS = ['priority_model', 'risk_model', 'impact_model']

    def __init__(self, model_dir: str | None = None):
        self.model_dir = model_dir or settings.MODEL_DIR
        self.predictor = RailBlockPredictor(model_dir)

    def initialize(self):
        """Ensure model directory exists and initialize predictor with available models."""
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)
        try:
            self.predictor.initialize()
        except Exception as e:
            logger.warning(f"Predictor initialization warning: {e}")

    def get_predictor(self) -> RailBlockPredictor:
        """Return the predictor instance."""
        return self.predictor

    def train_all_models(self, training_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Train all 3 AI models (Priority, Risk, Impact), save them to self.model_dir,
        update metadata.json, re-initialize the predictor, and return training metrics.
        """
        try:
            if not os.path.exists(self.model_dir):
                os.makedirs(self.model_dir, exist_ok=True)

            logger.info(f"Training all AI models in {self.model_dir}...")
            metadata = train_models(
                model_dir=self.model_dir,
                version='1',
                training_data=training_data
            )

            # Reload predictor with freshly trained models
            self.predictor.initialize()
            logger.info("Successfully trained all models and updated predictor.")
            return metadata
        except Exception as e:
            logger.error(f"Error training models: {e}", exc_info=True)
            raise RuntimeError(f"Model training failed: {str(e)}") from e

    def get_model_status(self) -> Dict[str, Any]:
        """
        Get status of all models by checking metadata and verifying that
        the corresponding model artifact files (.joblib) actually exist on disk.
        """
        meta_path = os.path.join(self.model_dir, 'metadata.json')
        metadata = {}
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Error reading metadata.json: {e}")
                metadata = {}

        version = metadata.get('version', '1') if isinstance(metadata, dict) else '1'
        status = {'version': version}

        for model_name in self.REQUIRED_MODELS:
            model_info = metadata.get(model_name, {}) if isinstance(metadata, dict) else {}
            model_version = model_info.get('version', version)
            expected_file = os.path.join(self.model_dir, f"{model_name}_v{model_version}.joblib")
            file_exists = os.path.isfile(expected_file) and os.path.getsize(expected_file) > 0

            status[model_name] = {
                'loaded': file_exists,
                'version': model_version,
                'file_exists': file_exists,
                'metrics': model_info.get('metrics', {})
            }

        return status

    def models_available(self) -> bool:
        """
        Check whether all required models are present, exist as valid files on disk,
        and are marked as loaded.
        """
        status = self.get_model_status()
        return all(status.get(k, {}).get('loaded', False) is True for k in self.REQUIRED_MODELS)
