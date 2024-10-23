import shutil
import os
import ffmpeg
import re
import platform
import subprocess

from config.Config import Config
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime


def check_file_exists(directory, key):
        return os.path.exists(os.path.join(directory, key))


def add_image(media_id, media_path, date_text):
    
    extension = get_file_extension(media_path)
    day, month, year = date_text.split(".")

    media_dir = f"{year}/{month}"
    media_name = f"F{year}{month}{day}_{media_id}{extension}"
    media_key = f"{media_dir}/{media_name}"
    
    destination_path = os.path.join(Config.MEDIA_DIR, media_key)
    destination_dir = os.path.dirname(destination_path)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    shutil.copy2(media_path, destination_path)

    thumbnail_key = f"{year}/P{year}{month}{day}_{media_id}.jpg"
    thumbnail_key = create_image_thumbnail(media_key, thumbnail_key)

    return media_key, thumbnail_key


def create_image_thumbnail(media_key, thumbnail_key):
    img = Image.open(os.path.join(Config.MEDIA_DIR, media_key))
    img.thumbnail((160, 160))

    thumbnail_path = os.path.join(Config.THUMBNAILS_DIR, thumbnail_key)
    directory = os.path.dirname(thumbnail_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    img.save(thumbnail_path, "JPEG")
    return thumbnail_key

def get_file_extension(file_path):
    return os.path.splitext(file_path)[1]

def get_file_type(file_path):
    
    image_extensions = [".png", ".jpg", ".jpeg"]
    video_extensions = [".mp4", ".avi", ".mov", ".mpg", ".wmv", ".3gp", ".asf"]
    sound_extensions = [".mp3", ".wav"]
    extension = get_file_extension(file_path)
    if extension in image_extensions:
        return 1
    elif extension in video_extensions:
        return 2
    elif extension in sound_extensions:
        return 3
    
def get_date_from_file_metadata(file_path):
    try:
        if get_file_type(file_path) == 1:
            image = Image.open(file_path)
            exif_data = image._getexif()
            
            if exif_data is not None:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal':
                        exif_date =  value
                        return convert_exif_date_to_date_text(exif_date)
        return ""
    except:
        return ""

def get_date_from_filename(file_path):
    
    filename = os.path.basename(file_path)
    
    # Regular expression to find YYYYMMDD pattern in the filename
    match = re.search(r"(\d{4})(\d{2})(\d{2})", filename)
    
    if match:
        year, month, day = match.groups()
        if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
            return f"{day}.{month}.{year}"
    
    return ""


def convert_exif_date_to_date_text(exif_date):
    date_obj = datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")
    return date_obj.strftime("%d.%m.%Y") 


def save_video_audio(media_data, path):
    
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, "wb") as media_file:
        media_file.write(media_data)


def play_video_audio(file_path):
    file_path = os.path.normpath(file_path)

    if platform.system() == "Windows":
        subprocess.run(f'start "" "{file_path}"', shell=True)
    
    elif platform.system() == "Darwin":
        subprocess.run(["open", file_path])
    
    else:
        subprocess.run(["xdg-open", file_path])


