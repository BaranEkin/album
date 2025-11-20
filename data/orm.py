from __future__ import annotations

from sqlalchemy import INTEGER, REAL, TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Album(Base):
    __tablename__ = "Album"

    album_id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    tag: Mapped[str] = mapped_column(TEXT, nullable=False)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    path: Mapped[str] = mapped_column(TEXT, nullable=False)


class Media(Base):
    __tablename__ = "Media"

    media_uuid: Mapped[str] = mapped_column(
        TEXT, primary_key=True, unique=True, nullable=False
    )
    created_at: Mapped[float] = mapped_column(REAL, nullable=False)
    created_by: Mapped[str] = mapped_column(TEXT, nullable=False)
    modified_at: Mapped[float | None] = mapped_column(REAL)
    modified_by: Mapped[str | None] = mapped_column(TEXT)
    status: Mapped[int] = mapped_column(INTEGER, nullable=False)
    topic: Mapped[str] = mapped_column(TEXT, nullable=False)
    title: Mapped[str] = mapped_column(TEXT, nullable=False)
    location: Mapped[str] = mapped_column(TEXT, nullable=False)
    date: Mapped[float] = mapped_column(REAL, nullable=False)
    date_text: Mapped[str] = mapped_column(TEXT, nullable=False)
    date_est: Mapped[int] = mapped_column(INTEGER, nullable=False)
    rank: Mapped[float] = mapped_column(REAL, nullable=False)
    type: Mapped[int] = mapped_column(INTEGER, nullable=False)
    extension: Mapped[str] = mapped_column(TEXT, nullable=False)
    private: Mapped[int] = mapped_column(INTEGER, nullable=False)
    people: Mapped[str | None] = mapped_column(TEXT)
    people_count: Mapped[int] = mapped_column(INTEGER, nullable=False)
    people_detect: Mapped[str | None] = mapped_column(TEXT)
    notes: Mapped[str | None] = mapped_column(TEXT)
    tags: Mapped[str | None] = mapped_column(TEXT)
    albums: Mapped[str | None] = mapped_column(TEXT)
