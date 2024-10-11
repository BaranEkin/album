import json


class Config:
    MEDIA_DIR = ""
    THUMBNAILS_DIR = ""
    S3_BUCKET_NAME = ""
    LOCAL_STORAGE_ENABLED = True

    @staticmethod
    def read_config():
        with open("res/config.json", "r") as f:
            config = json.load(f)

        for key, value in config.items():
            setattr(Config, key, value)
