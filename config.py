"""
Конфигурация приложения
"""
import os
from pathlib import Path

from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=True)


class Settings(BaseSettings):
    """
    Настройки приложения из переменных окружения
    """
    # Название проекта
    PROJECT_NAME: str = "HistorySounds"
    PROJECT_VERSION: str = "1.0.0"

    # Настройки базы данных
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/hs.db")

    # Дополнительные настройки
    API_V1_STR: str = "/api/v1"

    EXCEL_DATA_PATH: str = "data/history_sounds.xlsx"

settings = Settings()





