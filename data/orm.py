from sqlalchemy import Column, INTEGER, TEXT, REAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Album(Base):
    __tablename__ = "Album"

    album_id = Column(INTEGER, primary_key=True)
    tag = Column(TEXT, nullable=False)
    name = Column(TEXT, nullable=False)
    path = Column(TEXT, nullable=False)


class Media(Base):
    __tablename__ = "Media"

    media_uuid = Column(TEXT, primary_key=True, unique=True, nullable=False)
    created_at = Column(REAL, nullable=False)
    created_by = Column(TEXT, nullable=False)
    modified_at = Column(REAL)
    modified_by = Column(TEXT)
    status = Column(INTEGER, nullable=False)
    topic = Column(TEXT, nullable=False)
    title = Column(TEXT, nullable=False)
    location = Column(TEXT, nullable=False)
    date = Column(REAL, nullable=False)
    date_text = Column(TEXT, nullable=False)
    date_est = Column(INTEGER, nullable=False)
    rank = Column(REAL, nullable=False)
    type = Column(INTEGER, nullable=False)
    extension = Column(TEXT, nullable=False)
    private = Column(INTEGER, nullable=False)
    people = Column(TEXT)
    people_count = Column(INTEGER, nullable=False)
    people_detect = Column(TEXT)
    notes = Column(TEXT)
    tags = Column(TEXT)
    albums = Column(TEXT)
