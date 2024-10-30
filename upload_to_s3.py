import os
import argparse
import boto3
from botocore.exceptions import NoCredentialsError
from tqdm import tqdm

# Global bucket name
BUCKET = "album-2-bucket"


def upload_directory_to_s3(root_dir):
    """
    Uploads the contents of a local directory to an S3 bucket, preserving the structure.
    Only uploads files that do not already exist in the bucket.
    
    :param root_dir: The local path of the directory to upload.
    """
    s3_client = boto3.client('s3')

    # Collect all files to be uploaded
    files_to_upload = []
    for root, dirs, files in os.walk(root_dir):
        for file_name in files:
            local_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(local_path, root_dir).replace("\\", "/").replace("Foto", "")
            files_to_upload.append((local_path, relative_path))

    # Initialize the progress bar
    with tqdm(total=len(files_to_upload), desc="Uploading files", unit="file") as pbar:
        for local_path, s3_path in files_to_upload:
            try:
                # Check if the file already exists in the bucket
                s3_client.head_object(Bucket=BUCKET, Key=s3_path)
                print(f"File '{s3_path}' already exists in S3. Skipping upload.")
            except s3_client.exceptions.ClientError as e:
                # If the file does not exist (404 error), upload it
                if e.response['Error']['Code'] == '404':
                    try:
                        s3_client.upload_file(local_path, BUCKET, s3_path)
                    except NoCredentialsError:
                        print("Credentials not available")
                        return
                    except Exception as ex:
                        print(f"Error uploading {local_path}: {ex}")
                else:
                    print(f"Error checking existence of {s3_path}: {e}")
            # Update progress bar regardless of whether the file was skipped or uploaded
            pbar.update(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a local directory to an S3 bucket.")
    parser.add_argument("root_dir", type=str, help="The local path of the directory to upload.")
    args = parser.parse_args()

    upload_directory_to_s3(args.root_dir)
