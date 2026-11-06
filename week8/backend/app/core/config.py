from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
BACKEND_DIR = Path(__file__).resolve().parents[2]
class Settings(BaseSettings):
    app_name: str = "TaskFlow API"
    environment: str = "development"
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'data' / 'taskflow.db').as_posix()}"
    frontend_origin: str = "http://127.0.0.1:5173"
    model_config = SettingsConfigDict(env_file=(BACKEND_DIR.parent / ".env", BACKEND_DIR / ".env"), env_prefix="TASKFLOW_", extra="ignore")
@lru_cache
def get_settings() -> Settings: return Settings()
