"""
Настройка базы данных SQLite
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

# Создание движка базы данных
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Для SQLite
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация базы данных - создание/пересоздание таблиц"""
    with engine.connect() as conn:
        # dev only, need to remove later!
        conn.execute(text("DROP TABLE IF EXISTS task_list_tasks"))
        conn.execute(text("DROP TABLE IF EXISTS events"))
        conn.execute(text("DROP TABLE IF EXISTS songs"))
        conn.execute(text("DROP TABLE IF EXISTS song_event"))
        conn.commit()

    # Создаёт все таблицы, которые были импортированы и зарегистрированы в Base
    Base.metadata.create_all(bind=engine)