import shutil
import os
import re
import cv2
import numpy as np
import platform
import subprocess

from typing import Literal, Union
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

from config.config import Config
from logger import log


def check_file_exists(directory: str, key: str) -> bool:
    """Check if a file exists within a specified directory.

    Args:
        directory (str): The directory path where the file is expected.
        key (str): Key to check within the directory.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    # Use os.path.join for cross-platform path handling
    return os.path.exists(os.path.join(directory, key))


def add_media(media_uuid: str, media_path: Union[str, bytes, os.PathLike]):
    """Add a media to the media directory with a structured filename and create a thumbnail.
    Create directories if needed.

    Args:
        media_id (Union[str, bytes, os.PathLike]): The unique identifier for the media item.
        media_path (str): The source file path of the media.
    """
    # Ensure media_path is a string
    if not isinstance(media_path, str):
        media_path = str(media_path)

    extension = get_file_extension(media_path)
    media_key = f"{media_uuid}{extension}"

    # Ensure destination directory exists
    os.makedirs(Config.MEDIA_DIR, exist_ok=True)
    destination_path = os.path.join(Config.MEDIA_DIR, media_key)

    shutil.copy2(media_path, destination_path)

    thumbnail_key = f"{media_uuid}.jpg"

    # Ensure thumbnails directory exists
    os.makedirs(Config.THUMBNAILS_DIR, exist_ok=True)

    file_type = get_file_type(media_path)
    if file_type == 1:
        create_image_thumbnail(media_key, thumbnail_key)
    elif file_type == 2:
        create_video_thumbnail(media_key, thumbnail_key)


def create_image_thumbnail(media_key: str, thumbnail_key: str):
    """Create and save a thumbnail for an image.

    Args:
        media_key (str): Media key of the source image.
        thumbnail_key (str): Key for the thumbnail to be saved.
    """

    img = Image.open(os.path.join(Config.MEDIA_DIR, media_key))
    img.thumbnail((160, 160))

    thumbnail_path = os.path.join(Config.THUMBNAILS_DIR, thumbnail_key)

    img = img.convert("RGB")
    img.save(thumbnail_path, "JPEG")


def create_video_thumbnail(media_key: str, thumbnail_key: str):
    # Load video and extract the frame
    video = cv2.VideoCapture(os.path.join(Config.MEDIA_DIR, media_key))
    frame_number = 30
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = video.read()

    if success:
        # Process frame: resize, crop center, and add banners
        # Get original dimensions
        h, w = frame.shape[:2]
        width = 320
        height = 300

        # Scale the frame to keep aspect ratio with minimum dimension covering width or height
        scale_w = width / w
        scale_h = height / h
        scale = max(scale_w, scale_h)  # Ensure both dimensions fit

        new_w = int(w * scale)
        new_h = int(h * scale)
        resized_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Crop center 320x300
        start_x = (new_w - width) // 2
        start_y = (new_h - height) // 2
        cropped_frame = resized_frame[
            start_y : start_y + height, start_x : start_x + width
        ]

    else:
        cropped_frame = np.zeros((300, 320, 3), dtype=np.uint8)
        log(
            "file_ops.create_video_thumbnail",
            f"Video frame could not be extracted from '{media_key}'. Black thumbnail will be used.",
            level="warning",
        )

    # Load banner
    banner = cv2.imread(os.path.join("res", "icons", "video_banner.jpg"))

    # Stack banners and thumbnail horizontally
    thumbnail_image = np.hstack((banner, cropped_frame, banner))
    thumbnail_path = os.path.join(Config.THUMBNAILS_DIR, thumbnail_key)

    # Ensure the thumbnail directory exists
    os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

    # Save the final image
    cv2.imwrite(thumbnail_path, thumbnail_image)

    # Release resources
    video.release()


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
    extension = get_file_extension(file_path).lower()
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
                    if tag == "DateTimeOriginal":
                        exif_date = value
                        return convert_exif_date_to_date_text(exif_date)
        return ""
    except Exception:
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


def open_with_default_app(file_path: Union[str, bytes, os.PathLike]):
    """Open a media file using the default system application.

    Args:
        file_path (Union[str, bytes, os.PathLike]): The path to the media file to be played.
    """

    try:
        # Convert to string if it's a PathLike object
        if not isinstance(file_path, str):
            file_path = str(file_path)

        # Check the operating system
        if platform.system() == "Windows":
            # Windows-specific method
            os.startfile(file_path)
        elif platform.system() == "Darwin":
            # macOS-specific method
            subprocess.run(["open", file_path], check=True)
        else:
            # Linux - just use the system command directly
            # This is the most reliable way to open files on Linux
            os.system(f"xdg-open '{file_path}' &")
    except Exception as e:
        log(
            "file_ops.open_with_default_app",
            f"Error opening '{file_path}': {e}",
            level="error",
        )


def delete_media(media_uuid: str, extension: str) -> bool:
    media_key = f"{media_uuid}{extension}"
    media_path = os.path.join(Config.MEDIA_DIR, media_key)

    thumbnail_key = f"{media_uuid}.jpg"
    thumbnail_path = os.path.join(Config.THUMBNAILS_DIR, thumbnail_key)

    try:
        os.remove(media_path)
        os.remove(thumbnail_path)
        log(
            "file_ops.delete_media",
            f"Removed media with uuid:'{media_uuid}'",
            level="info",
        )
        return True
    except Exception as e:
        log(
            "file_ops.delete_media",
            f"Error removing media with uuid:'{media_uuid}': {e}",
            level="error",
        )
        return False


def delete_file(path) -> bool:
    """Delete a file at the specified path.

    Args:
        path: Path to the file to be deleted.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    try:
        # Convert to string if it's a PathLike object
        if not isinstance(path, str):
            path = str(path)

        os.remove(path)
        log("file_ops.delete_file", f"Deleted the file at:'{path}'", level="info")
        return True
    except Exception as e:
        log(
            "file_ops.delete_file",
            f"Error deleting the file at:'{path}': {e}",
            level="error",
        )
        return False


def copy_file(
    source_path: Union[str, bytes, os.PathLike],
    destination_path: Union[str, os.PathLike],
) -> bool:
    """Copy a file from source to destination.

    Args:
        source_path: Path to the source file.
        destination_path: Path where the file should be copied.

    Returns:
        bool: True if copy was successful, False otherwise.
    """
    try:
        # Convert to string if they're PathLike objects
        if not isinstance(source_path, str):
            source_path = str(source_path)
        if not isinstance(destination_path, str):
            destination_path = str(destination_path)

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        shutil.copy2(source_path, destination_path)
        log(
            "file_ops.copy_file",
            f"Copied file from '{source_path}' to '{destination_path}'",
            level="info",
        )
        return True
    except Exception as e:
        log(
            "file_ops.copy_file",
            f"Error copying file from '{source_path}' to '{destination_path}': {e}",
            level="error",
        )
        return False
