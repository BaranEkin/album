import boto3
from botocore.signers import CloudFrontSigner
from io import BytesIO
from PIL import Image
from urllib import request
import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from config.Config import Config

sts = boto3.client("sts")


def get_user_id():
    user_id = sts.get_caller_identity()["UserId"]
    return user_id


def get_user_name():
    arn = sts.get_caller_identity()["Arn"]
    user_name = arn[arn.rfind("/") + 1:]
    return user_name


def rsa_signer(message):
    # Load the private key from the .pem file
    with open(Config.CLOUDFRONT_KEY_PATH, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )

    # Sign the message (URL) using the private key and SHA-1
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA1(),
    )
    return signature


def create_signed_url(url, expiration_date):
    cloudfront_signer = CloudFrontSigner(Config.CLOUDFRONT_KEY_ID, rsa_signer)
    return cloudfront_signer.generate_presigned_url(
        url, date_less_than=expiration_date
    )


def get_image_from_cloudfront(image_key):

    url = f"https://{Config.CLOUDFRONT_DOMAIN}/{image_key}"
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    signed_url = create_signed_url(url, expiration)

    try:
        with request.urlopen(signed_url) as response:
            image_data = response.read()
            image = Image.open(BytesIO(image_data))
            image = image.convert('RGB') if image.mode != 'RGB' else image
            return image
    except Exception as e:
        print(f"Error occurred: {e}")