import pandas as pd
from sqlalchemy import create_engine, Column, INTEGER, TEXT, REAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Define the base class for declarative table models
Base = declarative_base()


# Define the SQLAlchemy model matching the CSV structure
class Media(Base):
    __tablename__ = "Media"

    media_id = Column(INTEGER, primary_key=True, unique=True, nullable=False)
    title = Column(TEXT, nullable=False)
    location = Column(TEXT, nullable=False)
    date = Column(REAL, nullable=False)
    date_text = Column(TEXT, nullable=False)
    date_est = Column(INTEGER, nullable=False)
    thumbnail_key = Column(TEXT, nullable=False, unique=True)
    media_key = Column(TEXT, nullable=False, unique=True)
    type = Column(INTEGER, nullable=False)
    extension = Column(TEXT, nullable=False)
    private = Column(INTEGER, nullable=False)
    people = Column(TEXT)
    people_count = Column(INTEGER, nullable=False)
    notes = Column(TEXT)
    tags = Column(TEXT)
    albums = Column(TEXT)


def date_to_julian(date_str: str) -> float:
    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
    julian_day = date_obj.toordinal() + 1721424.5
    return julian_day


def make_entry(old_entry):
    title = old_entry["BASLIK"]
    location = old_entry["YER"]
    date = date_to_julian(old_entry["ZAMAN"])
    date_text = old_entry["ZAMAN"]
    date_est = old_entry["YAKTARIH"]
    thumbnail_key = old_entry["GORUNTU"][1:].replace("\\", "/").replace("P", "T")
    media_key = old_entry["DOSYAADI"][5:].replace("\\", "/").replace("F", "M")
    mtype = old_entry["DOSYATIPI"]
    extension = old_entry["UZANTI"]
    private = old_entry["OZEL"]
    people = old_entry["KISILER"]
    people_count = old_entry["KISIADET"]
    notes = old_entry["NOTLAR"] or ""
    albums = old_entry["ALBUMS"]
    tags = ""  # GPT?

    return Media(title=title, location=location, date=date, date_text=date_text,
                 date_est=date_est, thumbnail_key=thumbnail_key, media_key=media_key,
                 type=mtype, extension=extension, private=private, people=people,
                 people_count=people_count, notes=notes, albums=albums, tags=tags)


if __name__ == "__main__":
    # Create an SQLite database engine (or connect to the existing one)
    engine = create_engine("sqlite:///res/database/album.db")

    Session = sessionmaker(bind=engine)
    session = Session()

    # Read the CSV file
    csv_file_path = "res/database/ALBUM_20200503.csv"
    df = pd.read_csv(csv_file_path, delimiter=";", encoding="utf-8")

    # Iterate over the rows of the CSV and insert them into the SQLite database
    for i, row in df.iterrows():
        print(i)
        media_entry = make_entry(row)
        session.add(media_entry)

    # Commit the session to save the changes
    session.commit()

    # Close the session
    session.close()
