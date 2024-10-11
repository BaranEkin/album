import boto3
from io import BytesIO
from PIL import Image
from config.Config import Config

s3 = boto3.client("s3")
sts = boto3.client("sts")


def download_image_from_s3(image_key):
    print(f"Downloading image data {image_key} from AWS S3 bucket.")
    image_data = BytesIO()
    s3.download_fileobj(Config.S3_BUCKET_NAME, image_key, image_data)
    print("Image data downloaded.")
    image_data.seek(0)
    image = Image.open(image_data)
    image = image.convert('RGB') if image.mode != 'RGB' else image
    print("Returning the PIL image.")
    return image


def get_user_id():
    user_id = sts.get_caller_identity()["UserId"]
    return user_id


def get_user_name():
    arn = sts.get_caller_identity()["Arn"]
    user_name = arn[arn.rfind("/") + 1:]
    return user_name
