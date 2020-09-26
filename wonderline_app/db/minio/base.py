import json
import logging
import os

from minio import ResponseError, Minio
from minio.error import NoSuchKey

from wonderline_app.db.minio.exceptions import MinioObjectSavingError

LOGGER = logging.getLogger(__name__)


def create_read_only_policy(bucket_name: str):
    resource = f"arn:aws:s3:::{bucket_name}"
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetBucketLocation",
                    "Resource": resource
                },
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:ListBucket",
                    "Resource": resource
                },
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": resource + "/*"
                }
            ]
        }
    )


def create_minio_bucket(bucket_name: str, location: str = "us-east-1"):
    # TODO: config SSL connection (secure=False)
    #       see related Github issue https://github.com/minio/minio/issues/6820
    minio_client = get_minio_client()
    policy = create_read_only_policy(bucket_name)
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name, location=location)
            minio_client.set_bucket_policy(bucket_name=bucket_name, policy=policy)
            LOGGER.info(f"Minio bucket {bucket_name} created")
            LOGGER.debug(f"Policy: {minio_client.get_bucket_policy(bucket_name=bucket_name)}")
    except ResponseError as err:
        LOGGER.error(f"Error while creating minio bucket \n"
                     f"bucket name: {bucket_name}\n"
                     f"policy: {policy}\n"
                     f"location: {location}")
        LOGGER.exception(err)


def get_minio_client():
    minio_client = Minio(
        endpoint=os.environ['MINIO_HOST'] + ':' + os.environ['MINIO_PORT'],
        access_key=os.environ['MINIO_ACCESS_KEY'],
        secret_key=os.environ['MINIO_SECRET_KEY'],
        secure=False)
    return minio_client


def put_object_in_minio_and_return_url(bucket_name: str, object_name: str, file_path: str):
    minio_client = get_minio_client()
    try:
        LOGGER.info(f"Saving the file {file_path} into minio with the "
                    f"object name: {object_name} ...")
        minio_client.fput_object(bucket_name=bucket_name, object_name=object_name,
                                 file_path=file_path)
    except ResponseError as err:
        LOGGER.exception(err)
        raise MinioObjectSavingError(f"Failed to save object {object_name}")
    else:
        return "http://localhost" + "/" + bucket_name + "/" + object_name


def object_exists_in_minio(bucket_name: str, object_name: str):
    minio_client = get_minio_client()
    try:
        minio_object = minio_client.stat_object(bucket_name=bucket_name, object_name=object_name)
    except NoSuchKey:
        return False
    return minio_object is not None
