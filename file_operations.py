import shutil
import os
import re
import platform
import subprocess

from typing import Literal, Union
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

from config.config import Config


def check_file_exists(directory: str, key: str) -> bool:
    """Check if a file exists within a specified directory.

    Args:
        directory (str): The directory path where the file is expected.
        key (str): Key to check within the directory.

    Returns:
        bool: True if the file exists, False otherwise.
    """

    return os.path.exists(os.path.join(directory, key))


def add_image(media_id: str, media_path: Union[str, bytes, os.PathLike], date_text: str) -> tuple[str, str]:
    """Add an image to the media directory with a structured filename and create a thumbnail.
    Crate directories if needed.

    Args:
        media_id (Union[str, bytes, os.PathLike]): The unique identifier for the media item.
        media_path (str): The source file path of the media.
        date_text (str): The date in 'DD.MM.YYYY' format for organizing the file.

    Returns:
        tuple: A tuple containing the media key  and the thumbnail key.
    """

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


def create_image_thumbnail(media_key: str, thumbnail_key: str) -> str:
    """Create and save a thumbnail for an image.

    Args:
        media_key (str): Media key of the source image.
        thumbnail_key (str): Key for the thumbnail to be saved.

    Returns:
        str: The key of the created thumbnail.
    """

    img = Image.open(os.path.join(Config.MEDIA_DIR, media_key))
    img.thumbnail((160, 160))

    thumbnail_path = os.path.join(Config.THUMBNAILS_DIR, thumbnail_key)
    directory = os.path.dirname(thumbnail_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    img.save(thumbnail_path, "JPEG")
    return thumbnail_key


def get_file_extension(file_path: Union[str, bytes, os.PathLike]) -> str:
    """Retrieve the file extension from a given file path.

    Args:
        file_path (Union[str, bytes, os.PathLike]): The path of the file.

    Returns:
        str: The file extension, including the leading dot.
    """

    return os.path.splitext(file_path)[1]


def get_file_type(file_path: Union[str, bytes, os.PathLike]) -> Literal[1, 2, 3]:
    """Determine the type of file based on its extension.

    Args:
        file_path (Union[str, bytes, os.PathLike]): The path of the file to check.

    Returns:
        int: A code representing the file type:
            - 1 for image files
            - 2 for video files
            - 3 for sound files
    """

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


def get_date_from_file_metadata(file_path: Union[str, bytes, os.PathLike]):
    """Extract the original date from the file's metadata if available.

    Args:
        file_path (Union[str, bytes, os.PathLike]): The path of the image file.

    Returns:
        str: The extracted date as a text string if present, or an empty string if
             no date metadata is found or an error occurs.
    """

    try:
        if get_file_type(file_path) == 1:
            image = Image.open(file_path)
            exif_data = image._getexif()

            if exif_data is not None:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal':
                        exif_date = value
                        return convert_exif_date_to_date_text(exif_date)
        return ""
    except Exception as e:
        return ""


def get_date_from_filename(file_path: Union[str, bytes, os.PathLike]):
    """Extract a date in the format DD.MM.YYYY from a filename if present.

    Args:
        file_path (Union[str, bytes, os.PathLike]): The path of the file whose filename is analyzed.

    Returns:
        str: The extracted date in the format 'DD.MM.YYYY' if a valid date
             pattern (YYYYMMDD) is found; otherwise, an empty string.
    """

    filename = os.path.basename(file_path)

    # Regular expression to find YYYYMMDD pattern in the filename
    match = re.search(r"(\d{4})(\d{2})(\d{2})", filename)

    if match:
        year, month, day = match.groups()
        if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
            return f"{day}.{month}.{year}"

    return ""


def convert_exif_date_to_date_text(exif_date):
    """Convert an EXIF date string to a formatted date text.

    Args:
        exif_date (str): The EXIF date string in the format 'YYYY:MM:DD HH:MM:SS'.

    Returns:
        str: The formatted date as 'DD.MM.YYYY'.
    """

    date_obj = datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")
    return date_obj.strftime("%d.%m.%Y")


def save_video_audio(media_data, path: Union[str, bytes, os.PathLike]):
    """Save binary media data to a specified file path, creating directories if needed.

    Args:
        media_data (bytes): The binary media data to save.
        path (Union[str, bytes, os.PathLike]): The file path where the media data will be saved.
    """

    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, "wb") as media_file:
        media_file.write(media_data)


def play_video_audio(file_path: Union[str, bytes, os.PathLike]):
    """Play a media file using the default system application based on the operating system.

    Args:
        file_path (Union[str, bytes, os.PathLike]): The path to the media file to be played.
    """

    file_path = os.path.normpath(file_path)

    if platform.system() == "Windows":
        subprocess.run(f'start "" "{file_path}"', shell=True)

    elif platform.system() == "Darwin":
        subprocess.run(["open", file_path])

    else:
        subprocess.run(["xdg-open", file_path])
