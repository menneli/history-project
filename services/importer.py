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
import pandas as pd
from sqlalchemy import func
import re


def normalize_event_id(raw_id) -> str:
    if pd.isna(raw_id):
        return None
    try:
        return str(int(float(raw_id)))
    except (ValueError, TypeError):
        return str(raw_id).strip() if raw_id else None

def extract_year(raw_val):
    """Safely extract year from dates like '19.04.1917', Excel date objects, or NaN."""
    if pd.isna(raw_val):
        return None
    try:
        # Pandas handles Excel dates, 'DD.MM.YYYY', 'YYYY-MM-DD', etc.
        return pd.to_datetime(raw_val, dayfirst=True).year
    except Exception:
        # Fallback: grab first 4-digit year (19xx or 20xx) from string
        match = re.search(r'\b(19|20)\d{2}\b', str(raw_val))
        return int(match.group(0)) if match else None


def import_songs_from_excel(file_path: str | Path, sheet_name: str = "music") -> dict:
    """Parse Excel and insert songs into DB. Returns import stats."""
    db = SessionLocal()
    try:
        songs_data = parse_songs_excel(file_path, sheet_name=sheet_name)
        stats = {"imported": 0, "skipped_duplicates": 0, "errors": 0, "skipped_empty": 0}

        for song_in in songs_data:
            # Safely extract & clean fields
            name = str(getattr(song_in, 'name', '') or '').strip()
            composer = str(getattr(song_in, 'composer', '') or '').strip()
            description = str(getattr(song_in, 'description', '') or '').strip()

            # Skip rows where name is missing, empty, or NaN
            if not name or name.lower() in ('nan', 'none', ''):
                stats["skipped_empty"] += 1
                continue

            # Normalize composer
            if composer.lower() in ('nan', 'none', ''):
                composer = ""

            # Clean description: skip if it's NaN/None/empty
            if description.lower() in ('nan', 'none', ''):
                description = None

            try:
                existing = db.query(Song).filter(
                    Song.name == name,
                    Song.composer == composer
                ).first()

                if not existing:
                    db_song = Song(
                        name=name,
                        composer=composer,
                        description=description
                    )
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


def import_events_from_excel(file_path: str | Path, sheet_name: str = "events") -> dict:
    """Parse Excel events sheet & insert into DB. Returns import stats."""
    from services.parser import _clean_and_rename_columns
    db = SessionLocal()
    try:
        events_df = pd.read_excel(file_path, sheet_name=sheet_name)
        events_df = _clean_and_rename_columns(events_df)
        stats = {"imported": 0, "skipped_duplicates": 0, "errors": 0}

        for _, row in events_df.iterrows():
            try:
                desc = row.get("description")
                excel_id = row.get("event_id")
                raw_title = row.get("title")

                if pd.isna(desc):
                    continue

                title = str(raw_title).strip() if pd.notna(raw_title) else None
                raw_start = row.get("year_start")
                raw_end = row.get("year_end")

                year_start = None
                if pd.notna(raw_start):
                    try:
                        year_start = extract_year(raw_start)
                    except:
                        pass

                year_end = None
                if pd.notna(raw_end):
                    try:
                        year_end = extract_year(raw_end)
                    except:
                        pass

                # Check for duplicates by description
                existing = db.query(Event).filter(Event.description == str(desc).strip()).first()
                if existing:
                    stats["skipped_duplicates"] += 1
                    continue

                # Save with both year fields
                db_event = Event(
                    description=str(desc).strip(),
                    title=title,
                    excel_id=normalize_event_id(excel_id),
                    year_start=year_start,
                    year_end=year_end,
                )
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

def link_songs_to_events(file_path: str | Path, sheet_songs="music", sheet_events="events") -> dict:
    from services.parser import _clean_and_rename_columns

    db = SessionLocal()
    try:
        songs_df = pd.read_excel(file_path, sheet_name=sheet_songs)
        songs_df = _clean_and_rename_columns(songs_df)

        event_map = {}
        for event in db.query(Event).filter(Event.excel_id != None).all():
            raw = str(event.excel_id)
            try:
                clean = str(int(float(raw)))
            except:
                clean = raw.strip()
            event_map[clean] = event

        stats = {"linked": 0, "skipped_no_id": 0, "skipped_no_song": 0, "errors": 0}

        for _, row in songs_df.iterrows():
            song_name = row.get("name")
            composer = row.get("composer")
            event_ids_raw = row.get("event_id")

            if pd.isna(event_ids_raw) or pd.isna(song_name):
                stats["skipped_no_id"] += 1
                continue

            db_song = db.query(Song).filter(
                Song.name == str(song_name).strip(),
                Song.composer == str(composer).strip()
            ).first()

            if not db_song:
                stats["skipped_no_song"] += 1
                continue

            # Parse IDs: handle "1.0", "1, 2", "1 2", etc.
            ids = str(event_ids_raw).replace(",", " ").split()
            for eid in ids:
                eid_clean = normalize_event_id(eid)
                if not eid_clean:
                    continue
                if eid_clean in event_map:
                    ev = event_map[eid_clean]
                    if ev not in db_song.events:
                        db_song.events.append(ev)
                        stats["linked"] += 1
                else:
                    stats["skipped_no_id"] += 1

        db.commit()
        return stats
    except Exception as e:
        db.rollback()
        print(f" Linking error: {e}")
        raise RuntimeError(f"Event linking failed: {e}") from e
    finally:
        db.close()