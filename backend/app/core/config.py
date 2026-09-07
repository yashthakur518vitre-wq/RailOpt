from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve paths from the project itself, not from the directory used to start Uvicorn.
# This prevents SQLite/model paths from changing when the user runs the backend from
# backend\app, backend, or another working directory.
BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BACKEND_DIR / "railblock.db"
DEFAULT_MODEL_DIR = BACKEND_DIR / "ml_models"


def _normalise_sqlite_url(value: str) -> str:
    """Turn a relative SQLite URL into a path relative to the backend directory."""
    if not value.startswith("sqlite:///"):
        return value

    raw = value[len("sqlite:///"):]
    # Keep SQLite memory databases and already-absolute URLs unchanged.
    if raw in {":memory:", ""}:
        return value

    path = Path(raw)
    if not path.is_absolute():
        path = BACKEND_DIR / path
    return f"sqlite:///{path.resolve().as_posix()}"


class Settings(BaseSettings):
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
    FRONTEND_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    MODEL_DIR: str = str(DEFAULT_MODEL_DIR)
    LOG_LEVEL: str = "INFO"
    OPTIMIZER_TIME_LIMIT: int = 30
    APP_NAME: str = "RailBlock AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DATABASE_URL = _normalise_sqlite_url(self.DATABASE_URL)
        model_path = Path(self.MODEL_DIR)
        if not model_path.is_absolute():
            model_path = BACKEND_DIR / model_path
        self.MODEL_DIR = str(model_path.resolve())


settings = Settings()
