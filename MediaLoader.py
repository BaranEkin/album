import os

from PyQt5.QtGui import QImage

import aws
from config.Config import Config
from PIL import Image


class MediaLoader:
    def __init__(self):
        self.media_dir = Config.MEDIA_DIR
        self.thumbnails_dir = Config.THUMBNAILS_DIR
        self.local_storage_enabled = Config.LOCAL_STORAGE_ENABLED

    def get_image(self, image_key):
        if self.check_local_storage(self.media_dir, image_key):
            print("Image is found on local storage.")
            try:
                image = QImage(os.path.join(self.media_dir, image_key))
                print("Image retrieved from local storage.")
                return image
            except OSError as e:
                print(f"Image retrieval failed on local storage: {e}")
                pass

        else:
            print("Image is not found on local storage.")
            try:
                pil_image = aws.get_image_from_cloudfront(image_key, prefix="media/")
                print("Image retrieved from AWS S3 bucket.")
                if self.local_storage_enabled:
                    try:
                        print("Image will be saved to local storage.")
                        self.save_image(pil_image, image_key)
                        print("Image saved to local storage.")
                        image = QImage(os.path.join(self.media_dir, image_key))
                        print("Image retrieved from local storage.")

                    except OSError as e:
                        print(
                            f"Image retrieval failed on local storage after AWS S3: {e}"
                        )
                        image = QImage(
                            pil_image.tobytes(),
                            pil_image.size[0],
                            pil_image.size[1],
                            QImage.Format_RGB888,
                        )
                        print("Image is directed from AWS S3 bucket.")

                    return image

            except Exception as e:
                print(f"Image retrieval failed on cloud storage: {e}")
                pass

    def get_thumbnail(self, thumbnail_key):
        if self.check_local_storage(self.thumbnails_dir, thumbnail_key):
            try:
                image = QImage(os.path.join(self.thumbnails_dir, thumbnail_key))
                return image
            except OSError as e:
                pass

        else:
            print(f"Thumbnail is not found on local storage: {thumbnail_key}")
            try:
                pil_image = aws.get_image_from_cloudfront(thumbnail_key, prefix="thumbnails/")
                try:
                    self.save_thumbnail(pil_image, thumbnail_key)
                    image = QImage(os.path.join(self.thumbnails_dir, thumbnail_key))

                except OSError as e:
                    image = QImage(
                        pil_image.tobytes(),
                        pil_image.size[0],
                        pil_image.size[1],
                        QImage.Format_RGB888,
                    )

                return image

            except Exception as e:
                pass

    def save_image(self, image: Image, image_key):
        path = os.path.join(self.media_dir, image_key)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        image.save(path, "JPEG")

    def save_thumbnail(self, image: Image, thumbnail_key):
        path = os.path.join(self.thumbnails_dir, thumbnail_key)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        image.save(path, "JPEG")

    @staticmethod
    def check_local_storage(directory, key):
        return os.path.exists(os.path.join(directory, key))
