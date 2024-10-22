import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import aws
from data.Media import Media
from data.helpers import date_to_julian, legacy_time_in_unix_subsec, current_time_in_unix_subsec


def make_entry(old_entry, user_name):
    title = old_entry["BASLIK"]
    location = old_entry["YER"]
    date = date_to_julian(old_entry["ZAMAN"])
    date_text = old_entry["ZAMAN"]
    date_est = old_entry["YAKTARIH"]
    thumbnail_key = old_entry["GORUNTU"][1:].replace("\\", "/")
    media_key = old_entry["DOSYAADI"][5:].replace("\\", "/")
    mtype = old_entry["DOSYATIPI"]
    extension = old_entry["UZANTI"]
    private = old_entry["OZEL"]
    people = old_entry["KISILER"]
    people_count = old_entry["KISIADET"]
    people_detect = "" # Face Detections
    notes = old_entry["NOTLAR"] or ""
    albums = old_entry["ALBUMS"]
    tags = ""  # GPT?

    created_at = legacy_time_in_unix_subsec(old_entry["KAYITZAMAN"])
    media_id = str(created_at).replace(".", "_")
    if media_id in MEDIA_IDS:
        created_at += 0.1
        media_id = str(created_at).replace(".", "_")

    MEDIA_IDS.append(media_id)

    modified_at = current_time_in_unix_subsec()

    return Media(title=title, 
                 location=location, 
                 date=date, 
                 date_text=date_text,
                 date_est=date_est, 
                 thumbnail_key=thumbnail_key, 
                 media_key=media_key,
                 type=mtype, 
                 extension=extension, 
                 private=private, 
                 people=people,
                 people_count=people_count, 
                 people_detect=people_detect, 
                 notes=notes, 
                 albums=albums, 
                 tags=tags,
                 created_at=created_at, 
                 modified_at = modified_at,
                 user_name=user_name, 
                 media_id=media_id)


if __name__ == "__main__":
    MEDIA_IDS = []
    user_name = aws.get_user_name()

    # Create an SQLite database engine (or connect to the existing one)
    engine = create_engine("sqlite:///res/database/album.db")

    Session = sessionmaker(bind=engine)
    session = Session()

    # Read the CSV file
    csv_file_path = "res/database/ALBUM_test.csv"
    df = pd.read_csv(csv_file_path, delimiter=";", encoding="utf-8")

    # Iterate over the rows of the CSV and insert them into the SQLite database
    for i, row in df.iterrows():
        media_entry = make_entry(row, user_name)
        session.add(media_entry)

    session.commit()

    # Close the session
    session.close()
