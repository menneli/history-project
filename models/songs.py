from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database.db import Base
from models.connection import song_event

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    composer = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    composer_info = Column(String, nullable=True)
    link = Column(String, nullable=True)

    events = relationship("Event", secondary=song_event, back_populates="songs")