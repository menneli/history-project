from sqlalchemy import Table, Column, Integer, ForeignKey
from database.db import Base

song_event = Table(
    "song_event",
    Base.metadata,
    Column("song_id", Integer, ForeignKey("songs.id"), primary_key=True),
    Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
)