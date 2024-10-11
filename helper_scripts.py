from pathlib import Path
from PIL import Image
import os


def resize_thumbnails(folder_path):
    image_extensions = {".jpg", ".jpeg"}

    thumbnail_paths = [
        str(file)
        for file in folder_path.rglob("*")
        if file.suffix.lower() in image_extensions
    ]

    for i, path in enumerate(thumbnail_paths):
        try:
            img = Image.open(path)
            # img.thumbnail((160, 160))

            new_path = path.replace("\\Foto", "\\").replace("F", "M")
            directory = os.path.dirname(new_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            img.save(new_path, "JPEG")
            os.remove(path)
            print(i)

        except Exception as e:
            print(e)
            continue


if __name__ == "__main__":
    thumbnails_folder = Path("res/media")
    resize_thumbnails(thumbnails_folder)
