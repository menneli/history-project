import pandas as pd
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, ValidationError


RUSSIAN_COLUMN_MAP = {
    "композиция": "name",
    "автор": "composer",
    "id песни": "song_id",
    "краткое описание": "description",
    "id события": "event_id",
    "события в момент выхода композиции": "song_description"
}

def _clean_and_rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize headers: strip spaces, remove non-breaking spaces, lowercase, map to English"""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace('\xa0', ' ')
    )
    return df.rename(columns=RUSSIAN_COLUMN_MAP)

class SongImport(BaseModel):
    song_id: Optional[int] = None
    name: str
    composer: str
    description: Optional[str] = None

class EventImport(BaseModel):
    event_id: Optional[int] = None
    description: str


def parse_songs_excel(file_path: str | Path, sheet_name: str = "Songs") -> List[SongImport]:
    sheet_name = sheet_name.strip()

    available = pd.ExcelFile(file_path).sheet_names
    print(f"   Looking for sheet: '{sheet_name}'")
    print(f"   Available sheets: {available}")

    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = _clean_and_rename_columns(df)  # Renames columns to English keys

    songs = []
    for _, row in df.iterrows():
        try:
            # Use the RENAMED column key ("song_description")
            raw_desc = row.get("song_description")
            description = str(raw_desc).strip() if pd.notna(raw_desc) else None

            song = SongImport(
                song_id=int(row["song_id"]) if pd.notna(row.get("song_id")) else None,
                name=str(row["name"]).strip(),
                composer=str(row["composer"]).strip(),
                description=description
            )
            songs.append(song)
        except ValidationError as e:
            print(f"Skipping song row: {e}")
            continue
    return songs


def parse_events_excel(file_path: str | Path, sheet_name: str = "Events") -> List[EventImport]:
    sheet_name = sheet_name.strip()
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    df = _clean_and_rename_columns(df)

    events = []
    for _, row in df.iterrows():
        try:
            event = EventImport(
                event_id=int(row["event_id"]) if pd.notna(row.get("event_id")) else None,
                description=str(row["description"]).strip(),
            )
            events.append(event)
        except ValidationError as e:
            print(f"Skipping event row: {e}")
            continue
    return events