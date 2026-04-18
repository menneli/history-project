import sys
from pathlib import Path
from config import EXCEL_DATA_PATH

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
    print(f" EXCEL_DATA_PATH: {EXCEL_DATA_PATH}")

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

    excel_file = EXCEL_DATA_PATH

    #  DEBUG: Print absolute path and existence
    print(f" Checking Excel at: {Path(excel_file).resolve()}")
    print(f"   File exists: {Path(excel_file).exists()}")

    if not Path(excel_file).exists():
        print(f"    Excel file not found: {excel_file}")
        # List files in data/ dir for debugging
        data_dir = Path(excel_file).parent
        if data_dir.exists():
            print(f"    Contents of {data_dir}: {list(data_dir.iterdir())}")
        return

    if not Path(excel_file).exists():
        print(f"    Excel file not found: {Path(excel_file).absolute()}")
    else:
        print(f"    Source: {Path(excel_file).absolute()}")

        print("\n   Importing songs...")
        try:
            song_stats = import_songs_from_excel(excel_file, sheet_name="music")
            print(f"      Songs: {song_stats}")
        except Exception as e:
            print(f"      Failed: {e}")

        print("\n   Importing events...")
        try:
            event_stats = import_events_from_excel(excel_file, sheet_name="events")
            print(f"      Events: {event_stats}")
        except Exception as e:
            print(f"      Failed: {e}")

        print("\n DEBUG: Excel ID → Description samples")
        import pandas as pd
        from services.parser import _clean_and_rename_columns
        df_events = pd.read_excel(excel_file, sheet_name="events")
        df_events = _clean_and_rename_columns(df_events)
        df_songs = pd.read_excel(excel_file, sheet_name="music")
        df_songs = _clean_and_rename_columns(df_songs)

        print("\n Events sheet (first 3 rows):")
        for _, row in df_events.head(3).iterrows():
            print(f"   ID: '{row.get('event_id')}' | Desc: '{row.get('description')}'")

        print("\n Songs with event IDs (first 3 that have them):")
        songs_with_ids = df_songs[df_songs["event_id"].notna()].head(3)
        for _, row in songs_with_ids.iterrows():
            print(f"   Song: '{row.get('name')}' | Event IDs: '{row.get('event_id')}'")


        print("\n   Linking songs to events...")
        try:
            from services.importer import link_songs_to_events
            link_stats = link_songs_to_events(excel_file)
            print(f"      Links created: {link_stats['linked']}")
            print(f"      ️  Skipped (no ID match): {link_stats['skipped_no_id']}")
            print(f"      Skipped (song not in DB): {link_stats['skipped_no_song']}")
        except Exception as e:
            print(f"      Linking failed: {e}")

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