import os
import datetime
from typing import Union

import boto3

from io import BytesIO
from PIL import Image
from urllib import request

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

from botocore.signers import CloudFrontSigner
from botocore.exceptions import (
    NoCredentialsError,
    PartialCredentialsError,
    ClientError,
    EndpointConnectionError,
    ConnectionClosedError)

from config.config import Config
from logger import log

sts = boto3.client("sts")
s3 = boto3.client("s3")


def get_user_name() -> str:
    """Retrieve the AWS IAM username of the current user.

    Returns:
        str: The IAM username extracted from the caller's ARN.
    """

    arn = sts.get_caller_identity()["Arn"]
    user_name = arn[arn.rfind("/") + 1:]
    return user_name


def rsa_signer(message) -> bytes:
    """Sign a message using an RSA private key.

    Args:
        message (bytes): The message to be signed.

    Returns:
        bytes: The RSA signature of the message.
    """

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


def generate_signed_url(url: str, expiration_date) -> str:
    """Generate a signed URL with an expiration date for AWS CloudFront using private key (res/cloudfront.pem).

    Args:
        url (str): The URL to be signed.
        expiration_date (datetime): The expiration date and time for the signed URL.

    Returns:
        str: The signed URL with expiration constraints.
    """

    cloudfront_signer = CloudFrontSigner(Config.CLOUDFRONT_KEY_ID, rsa_signer)
    return cloudfront_signer.generate_presigned_url(
        url, date_less_than=expiration_date
    )


def get_image_from_cloudfront(image_key: str, prefix: str) -> Image:
    """Retrieve an image from CloudFront using a signed URL.

    Args:
        image_key (str): Media key of the image.
        prefix (str): The prefix path to the image (media/ or thumbnail/).

    Returns:
        PIL.Image: The retrieved image in RGB format.

    Raises:
        Exception: If an error occurs while fetching or processing the image.
    """

    url = f"https://{Config.CLOUDFRONT_DOMAIN}/{prefix}{image_key}"
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    signed_url = generate_signed_url(url, expiration)

    try:
        with request.urlopen(signed_url) as response:
            image_data = response.read()
            image = Image.open(BytesIO(image_data))
            image = image.convert('RGB') if image.mode != 'RGB' else image
            return image
    except Exception as e:
        print(f"Error occurred: {e}")
        raise e


def get_video_audio_from_cloudfront(media_key: str, prefix: str) -> bytes:
    """Retrieve video or audio data from CloudFront using a signed URL.

    Args:
        media_key (str): Media key of the video or audio.
        prefix (str): The prefix path to the image (media/ or thumbnail/).

    Returns:
        bytes: The binary data of the retrieved media file.

    Raises:
        Exception: If an error occurs while fetching the media data.
    """

    url = f"https://{Config.CLOUDFRONT_DOMAIN}/{prefix}{media_key}"
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    signed_url = generate_signed_url(url, expiration)

    try:
        with request.urlopen(signed_url) as response:
            data = response.read()
            return data
    except Exception as e:
        print(f"Error occurred: {e}")
        raise e


def check_s3() -> bool:
    """Check if the S3 bucket is accessible.

    Returns:
        bool: True if the S3 bucket is reachable, False otherwise.
    """

    try:
        s3.head_bucket(Bucket=Config.S3_BUCKET_NAME)
        log("cloud_ops.check_s3", f"Bucket: {Config.S3_BUCKET_NAME} is reached successfully.")
        return True

    except ClientError as e:
        log("cloud_ops.check_s3", f"Unable to reach bucket: {Config.S3_BUCKET_NAME}. Error: {e}", level="error")
        return False


def upload_to_s3_bucket(path: Union[str, bytes, os.PathLike], key, prefix=""):
    """Upload a file to a specified S3 bucket path with optional prefix.

    Args:
        path (Union[str, bytes, os.PathLike]): The local path of the file to upload.
        key (str): The name of the file in the S3 bucket.
        prefix (str, optional): Optional prefix path in the S3 bucket. Defaults to "".

    Raises:
        NoCredentialsError: If AWS credentials are missing.
        PartialCredentialsError: If AWS credentials are incomplete.
        ClientError: For AWS client-related issues such as access or bucket existence.
        FileNotFoundError: If the specified local file is not found.
        PermissionError: If there are insufficient permissions to read the file.
        Exception: For any other unexpected errors during upload.
    """

    if not os.path.isfile(path):
        log("cloud_ops.upload_to_s3_bucket", f"The file '{path}' does not exist.", level="error")
        raise FileNotFoundError()

    try:
        s3.upload_file(path, Config.S3_BUCKET_NAME, f"{prefix}{key}")
        log("cloud_ops.upload_to_s3_bucket", f"File {path} uploaded successfully to {prefix}{key}")

    except NoCredentialsError as e:
        log("cloud_ops.upload_to_s3_bucket", "Credentials not available for AWS.", level="error")
        raise e

    except PartialCredentialsError as e:
        log("cloud_ops.upload_to_s3_bucket", "Incomplete AWS credentials provided.", level="error")
        raise e

    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            log("cloud_ops.upload_to_s3_bucket", f"Access denied to the bucket.", level="error")

        elif e.response['Error']['Code'] == 'NoSuchBucket':
            log("cloud_ops.upload_to_s3_bucket", f"The specified bucket does not exist.", level="error")

        else:
            log("cloud_ops.upload_to_s3_bucket", f"Client error occurred: {e}", level="error")
        raise e

    except PermissionError as e:
        log("cloud_ops.upload_to_s3_bucket", f"Permission denied: Unable to read '{path}'", level="error")
        raise e

    except Exception as e:
        log("cloud_ops.upload_to_s3_bucket", f"An unexpected error occurred: {e}", level="error")
        raise e


def download_from_s3_bucket(key, path) -> bool:
    """Download a file from an S3 bucket to a specified local path.

    Args:
        key (str): The name of the file in the S3 bucket.
        path (str): The local destination path for the downloaded file.

    Returns:
        bool: True if the download is successful, False if a network error occurs.

    Raises:
        NoCredentialsError: If AWS credentials are missing.
        PartialCredentialsError: If AWS credentials are incomplete.
        ClientError: For AWS client-related issues, such as access or key existence.
        PermissionError: If there are insufficient permissions to write to the destination path.
        Exception: For any other unexpected errors during download.
    """

    try:
        s3.download_file(Config.S3_BUCKET_NAME, key, path)
        log("cloud_ops.download_from_s3_bucket", f"File downloaded successfully to {path}", level="info")
        return True

    except (EndpointConnectionError, ConnectionClosedError) as e:
        log("cloud_ops.download_from_s3_bucket", "Network connection error encountered.", level="warning")
        return False

    except NoCredentialsError as e:
        log("cloud_ops.download_from_s3_bucket", "Credentials not available for AWS.", level="error")
        raise e

    except PartialCredentialsError as e:
        log("cloud_ops.download_from_s3_bucket", "Incomplete AWS credentials provided.", level="error")
        raise e

    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            log("cloud_ops.download_from_s3_bucket", f"Access denied {key}.", level="error")

        elif e.response['Error']['Code'] == 'NoSuchKey':
            log("cloud_ops.download_from_s3_bucket", f"The specified object key does not exist: {key}.", level="error")

        else:
            log("cloud_ops.download_from_s3_bucket", f"Client error occurred: {e}", level="error")
        raise e

    except PermissionError as e:
        log("cloud_ops.download_from_s3_bucket", f"Permission denied: Unable to write to {path}.", level="error")
        raise e

    except Exception as e:
        log("cloud_ops.download_from_s3_bucket", f"An unexpected error occurred: {e}", level="error")
        raise e
