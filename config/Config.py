import json


class Config:
    MEDIA_DIR = ""
    THUMBNAILS_DIR = ""
    S3_BUCKET_NAME = ""
    LOCAL_STORAGE_ENABLED = True
    DATABASE_DIR = ""
    CLOUDFRONT_KEY_PATH = ""
    CLOUDFRONT_DOMAIN = ""
    CLOUDFRONT_KEY_ID = ""

    @staticmethod
    def read_config():
        with open("res/config.json", "r") as f:
            config = json.load(f)

        for key, value in config.items():
            setattr(Config, key, value)
