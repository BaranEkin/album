import uuid
import os
import shutil
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PIL import Image

import face_detection
from media_loader import MediaLoader

from config.config import Config
from data.orm import Media
from data.helpers import date_to_julian, legacy_time_in_unix_subsec, current_time_in_unix_subsec
from ops import cloud_ops, file_ops

Config.read_config()
media_loader = MediaLoader()


def get_people_detect_str(image_key, people):
    try:
        if not isinstance(people, str):
            return None

        image = media_loader.get_image(image_key)
        if Image is None:
            return None
        image.save("detect.jpg", "JPEG")
        image = Image.open("detect.jpg")
        people_list = people.split(",")
        if len(people_list) < 1:
            return None

        detections = face_detection.detect_people(image)

        if len(detections) == len(people_list):
            detections_str = ",".join(['-'.join(map(str, det[:4])) for det in detections])
            return detections_str

        return None
    except Exception as e:
        return None


def make_files(media_uuid, old_entry, foto_folder, preview_folder):
    media_source_path = os.path.join(foto_folder, old_entry["DOSYAADI"][1:])
    if file_ops.get_file_type(media_source_path) == 1:
        file_ops.add_image(media_uuid, media_source_path)
    else:
        media_destination_path = os.path.join("res/media/", f"{media_uuid}{file_ops.get_file_extension(media_source_path)}")
        shutil.copy2(media_source_path, media_destination_path)

        thumb_source_path = os.path.join(preview_folder, old_entry["GORUNTU"][1:])
        thumb_destination_path = os.path.join("res/thumbnails/", f"{media_uuid}{file_ops.get_file_extension(thumb_source_path)}")
        shutil.copy2(thumb_source_path, thumb_destination_path)

    return f"{media_uuid}{file_ops.get_file_extension(media_source_path)}"


def make_entry(old_entry, user_name, foto_folder, preview_folder):
    global last_rank
    global last_date

    media_uuid = str(uuid.uuid4().hex)
    media_path = make_files(media_uuid, old_entry, foto_folder, preview_folder)
    
    topic = old_entry["KONU"]
    title = old_entry["BASLIK"]
    location = old_entry["YER"]
    date = date_to_julian(old_entry["ZAMANTEXT"])
    date_text = old_entry["ZAMANTEXT"]
    date_est = old_entry["YAKTARIH"]
    mtype = old_entry["DOSYATIPI"]
    extension = old_entry["UZANTI"]
    private = old_entry["OZEL"]
    people = old_entry["KISILER"]
    people_count = old_entry["KISIADET"]
    people_detect = None # get_people_detect_str(media_path, people) if int(mtype) == 1 else None
    notes = old_entry["NOTLAR"]
    albums = old_entry["ALBUMS"]
    tags = None

    if date == last_date:
        rank = last_rank + 1.0
    else:
        rank = 1.0
    
    last_rank = rank
    last_date = date

    created_at = legacy_time_in_unix_subsec(old_entry["KAYITZAMAN"])
    modified_at = current_time_in_unix_subsec()

    return Media(title=title,
                 topic=topic,
                 location=location,
                 date=date,
                 date_text=date_text,
                 date_est=date_est,
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
                 modified_at=modified_at,
                 user_name=user_name,
                 media_uuid=media_uuid,
                 rank=rank)


last_rank = 1.0
last_date = 0.0
user_name = cloud_ops.get_user_name()

# Create an SQLite database engine (or connect to the existing one)
engine = create_engine("sqlite:///res/database/album.db")

Session = sessionmaker(bind=engine)
session = Session()

try:
    # Read the CSV file
    csv_file_path = "res/database/album_fixed.csv"
    foto_folder_path = "C:/ALBUM/FOTO/"
    preview_folder_path = "C:/ALBUM/Data/Preview/"

    df = pd.read_csv(csv_file_path, delimiter=";", encoding="utf-8")

    # Iterate over the rows of the CSV and insert them into the SQLite database
    for i, row in df.iterrows():
        try:
            print(f"ROW: {i}___")
            media_entry = make_entry(row, user_name, foto_folder=foto_folder_path, preview_folder=preview_folder_path)
            
        except Exception as e:
            print("ERROR OCCURED at FOTO_ID:", str(row["FOTO_ID"]))
            print("ERROR:", str(e))
            continue
        
        try:
            session.add(media_entry)
            session.commit()
            os.remove(os.path.join(foto_folder_path, row["DOSYAADI"][1:]))
            os.remove(os.path.join(preview_folder_path, row["GORUNTU"][1:]))
        except:
            continue

finally:
    
    # Close the session
    session.close()
