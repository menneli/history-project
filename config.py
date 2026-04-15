"""
Конфигурация приложения
"""
from pathlib import Path
from pydantic_settings import BaseSettings

if Path(".env").exists():
    from dotenv import load_dotenv
    load_dotenv(override=True)

PROJECT_ROOT = Path(__file__).resolve().parent

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
    EXCEL_DATA_PATH: str = str(PROJECT_ROOT / "data" / "history_sounds.xlsx")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}

settings = Settings()
