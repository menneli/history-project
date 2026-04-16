"""
Конфигурация приложения
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Safe .env loading (only if file exists)
if Path(".env").exists():
    from dotenv import load_dotenv

    load_dotenv(override=True)

# Compute Excel path at module level (works everywhere)
EXCEL_DATA_PATH = str(Path.cwd() / "data" / "history_sounds.xlsx")


class Settings(BaseSettings):
    PROJECT_NAME: str = "HistorySounds"
    PROJECT_VERSION: str = "1.0.0"

    # Database: Railway overrides via Dashboard Variables
    DATABASE_URL: str = "sqlite:///./data/hs.db"

    # Other settings
    API_V1_STR: str = "/api/v1"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow"
    }


settings = Settings()
