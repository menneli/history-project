import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parents[1]  # Goes up one level
sys.path.insert(0, str(ROOT_DIR))
from database.db import engine, init_db
from sqlalchemy import inspect

# Check if tables exist
inspector = inspect(engine)
if not inspector.get_table_names():
    print(" Tables not found! Initializing database...")
    from models import songs, events
    init_db()
    print("Database initialized!")

from database.db import SessionLocal
from models.songs import Song
from models.events import Event
from services.parser import parse_songs_excel, parse_events_excel
from pathlib import Path


def import_songs_from_excel(file_path: str | Path, sheet_name: str = "Музыка") -> dict:
    """Parse Excel and insert songs into DB. Returns import stats."""
    db = SessionLocal()
    try:
        songs_data = parse_songs_excel(file_path, sheet_name=sheet_name)
        stats = {"imported": 0, "skipped_duplicates": 0, "errors": 0}

        for song_in in songs_data:
            try:
                existing = db.query(Song).filter(
                    Song.name == song_in.name,
                    Song.composer == song_in.composer
                ).first()

                if not existing:
                    db_song = Song(name=song_in.name, composer=song_in.composer)
                    db.add(db_song)
                    stats["imported"] += 1
            except Exception as e:
                stats["errors"] += 1
                print(f"Song error: {e}")

        db.commit()
        return stats
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Song import failed: {e}") from e
    finally:
        db.close()


def import_events_from_excel(file_path: str | Path, sheet_name: str = "События") -> dict:
    """Parse Excel events sheet & insert into DB. Returns import stats."""
    db = SessionLocal()
    try:
        events_data = parse_events_excel(file_path, sheet_name=sheet_name)
        stats = {"imported": 0, "skipped_duplicates": 0, "errors": 0}

        for event_in in events_data:
            try:
                # Prevent duplicates by exact description match
                existing = db.query(Event).filter(Event.description == event_in.description).first()
                if existing:
                    stats["skipped_duplicates"] += 1
                    continue

                db_event = Event(description=event_in.description)

                db.add(db_event)
                stats["imported"] += 1
            except Exception as e:
                stats["errors"] += 1
                print(f"Failed to import event row: {e}")

        db.commit()
        return stats
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Event import failed: {e}") from e
    finally:
        db.close()