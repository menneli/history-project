import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))


def main():
    print("=" * 60)
    print(" HistorySounds - Database Setup & Import")
    print("=" * 60)

    # Step 0: Ensure data directory exists
    data_dir = ROOT_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    print(f"Data directory: {data_dir}")

    # Step 1: Debug .env loading
    from config import settings
    print(f"\nDATABASE_URL: {settings.DATABASE_URL}")
    print(f" EXCEL_DATA_PATH: {settings.EXCEL_DATA_PATH}")

    # Step 2: Import models
    from models import songs, events, connection

    # Step 3: initialize DB
    from database.db import init_db, engine
    init_db()

    db_path = Path(engine.url.database)
    print(f" Database: {db_path.absolute()}")
    print(f"File exists: {db_path.exists()}")

    # Step 4: Import Excel data
    print("\nImporting Excel data...")
    from services.importer import import_songs_from_excel, import_events_from_excel

    excel_file = Path(settings.EXCEL_DATA_PATH)

    if not excel_file.exists():
        print(f"    Excel file not found: {excel_file.absolute()}")
    else:
        print(f"    Source: {excel_file.absolute()}")

        print("\n   Importing songs...")
        try:
            song_stats = import_songs_from_excel(excel_file, sheet_name="Музыка")
            print(f"      Songs: {song_stats}")
        except Exception as e:
            print(f"      Failed: {e}")

        print("\n   Importing events...")
        try:
            event_stats = import_events_from_excel(excel_file, sheet_name="События")
            print(f"      Events: {event_stats}")
        except Exception as e:
            print(f"      Failed: {e}")

    # Step 5: Verify results
    print("\nFinal Database Status:")
    print("   " + "-" * 40)
    from database.db import SessionLocal
    from models.songs import Song
    from models.events import Event

    db = SessionLocal()
    song_count = db.query(Song).count()
    event_count = db.query(Event).count()
    db.close()

    print(f"   Total songs: {song_count}")
    print(f"   Total events: {event_count}")
    print("   " + "-" * 40)
    print("\nSetup complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()