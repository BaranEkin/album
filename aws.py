import os
import boto3
from botocore.signers import CloudFrontSigner
from botocore.exceptions import (
    NoCredentialsError, 
    PartialCredentialsError, 
    ClientError, 
    EndpointConnectionError, 
    ConnectionClosedError)

from io import BytesIO
from PIL import Image
from urllib import request
import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from config.Config import Config

sts = boto3.client("sts")
s3 = boto3.client("s3")


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


def get_image_from_cloudfront(image_key, prefix):

    url = f"https://{Config.CLOUDFRONT_DOMAIN}/{prefix}{image_key}"
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
        raise e
    
def get_video_audio_from_cloudfront(media_key, prefix):
    
    url = f"https://{Config.CLOUDFRONT_DOMAIN}/{prefix}{media_key}"
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    signed_url = create_signed_url(url, expiration)

    try:
        with request.urlopen(signed_url) as response:
            data = response.read()
            return data
    except Exception as e:
        print(f"Error occurred: {e}")
        raise e
    

def check_s3():
    try:
        s3.head_bucket(Bucket=Config.S3_BUCKET_NAME)
        return True
    
    except ClientError as e:
        print(f"Unable to reach bucket: {Config.S3_BUCKET_NAME}. Error: {e}")
        return False


def upload_to_s3_bucket(path, key, prefix=""):
    if not os.path.isfile(path):
        print(f"The file '{path}' does not exist.")
        return

    try:
        s3.upload_file(path, Config.S3_BUCKET_NAME, f"{prefix}{key}")
        print(f"File {path} uploaded successfully to {prefix}{key}")

    except NoCredentialsError as e:
        print("Credentials not available for AWS. Please check your AWS credentials.")
        raise e
    
    except PartialCredentialsError as e:
        print("Incomplete AWS credentials provided. Please check your AWS credentials.")
        raise e
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print(f"Access denied to the bucket. Please check your permissions.")
        
        elif e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"The specified bucket does not exist.")

        else:
            print(f"Client error occurred: {e}")
        raise e
    
    except FileNotFoundError as e:
        print(f"The specified file was not found: {path}.")
        raise e
    
    except PermissionError as e:
        print(f"Permission denied: Unable to read '{path}'. Check your file system permissions.")
        raise e
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e
    

def dowload_from_s3_bucket(key, path):
    try:
        s3.download_file(Config.S3_BUCKET_NAME, key, path)
        print(f"File downloaded successfully to {path}")
        return True

    except (EndpointConnectionError, ConnectionClosedError) as e:
        print("Network error: Connection issue encountered. Please check your internet connection.")
        return False
    
    except NoCredentialsError as e:
        print("Credentials not available for AWS. Please check your AWS credentials.")
        raise e
    
    except PartialCredentialsError as e:
        print("Incomplete AWS credentials provided. Please check your AWS credentials.")
        raise e
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print(f"Access denied to the bucket or object.")
        
        elif e.response['Error']['Code'] == 'NoSuchKey':
            print(f"The specified object key does not exist: {key}.")
        
        else:
            print(f"Client error occurred: {e}")
        raise e
    
    except PermissionError as e:
        print(f"Permission denied: Unable to write to {path}. Check your file system permissions.")
        raise e
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e
