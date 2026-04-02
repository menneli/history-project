from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.db import Base

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    composer = Column(String, nullable=False)

    events = relationship("Event", secondary="song_event", back_populates="songs")