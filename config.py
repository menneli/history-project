"""
Конфигурация приложения
"""
from pathlib import Path
from pydantic_settings import BaseSettings
import os

if Path(".env").exists():
    from dotenv import load_dotenv
    load_dotenv(override=True)

class Settings(BaseSettings):
    """
    Настройки приложения из переменных окружения
    """
    # Название проекта
    PROJECT_NAME: str = "HistorySounds"
    PROJECT_VERSION: str = "1.0.0"

    # Настройки базы данных
    DATABASE_URL: str = "sqlite:///./data/hs.db"

    # Дополнительные настройки
    API_V1_STR: str = "/api/v1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}

settings = Settings()
