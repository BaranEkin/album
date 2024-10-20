from sqlalchemy import Column, INTEGER, TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Album(Base):
    __tablename__ = 'Album'
    
    album_id = Column(INTEGER, primary_key=True)
    tag = Column(TEXT, nullable=False)
    name = Column(TEXT, nullable=False)
    path = Column(TEXT, nullable=False)

