from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.db import Base
from models.connection import song_event

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(String, nullable=False)
    excel_id = Column(String, index=True)
    songs = relationship("Song", secondary=song_event, back_populates="events")