import json
import logging
import os

import urllib3
from minio.error import S3Error
from minio import Minio

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
    minio_client = get_minio_client()
    policy = create_read_only_policy(bucket_name)
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name, location=None)
            minio_client.set_bucket_policy(bucket_name=bucket_name, policy=policy)
            LOGGER.info(f"Minio bucket {bucket_name} created")
            LOGGER.debug(f"Policy: {minio_client.get_bucket_policy(bucket_name=bucket_name)}")
    except S3Error as err:
        LOGGER.error(f"Error while creating minio bucket \n"
                     f"bucket name: {bucket_name}\n"
                     f"policy: {policy}\n"
                     f"location: {location}")
        LOGGER.exception(err)


def get_minio_client():
    minio_client = Minio(
        endpoint=os.environ['MINIO_HOST'] + ':' + os.environ['MINIO_PORT'],
        access_key=os.environ['MINIO_ROOT_USER'],
        secret_key=os.environ['MINIO_ROOT_PASSWORD'],
        secure=True,
        # To fix the error "certificate verify failed: unable to get local issuer certificate"
        # See: https://github.com/minio/minio-py/issues/1134
        http_client=urllib3.PoolManager(cert_reqs="CERT_NONE"),
    )
    return minio_client


def put_object_in_minio_and_return_url(bucket_name: str, object_name: str, file_path: str):
    minio_client = get_minio_client()
    try:
        LOGGER.info(f"Saving the file {file_path} into minio with the "
                    f"object name: {object_name} ...")
        minio_client.fput_object(bucket_name=bucket_name, object_name=object_name,
                                 file_path=file_path)
    except S3Error as err:
        LOGGER.exception(err)
        raise MinioObjectSavingError(f"Failed to save object {object_name}")
    else:
        return f"https://localhost:{os.environ['MINIO_PORT']}/{bucket_name}/{object_name}"


def object_exists_in_minio(bucket_name: str, object_name: str):
    minio_client = get_minio_client()
    try:
        minio_object = minio_client.stat_object(bucket_name=bucket_name, object_name=object_name)
    except S3Error:
        return False
    return minio_object is not None


def remove_object_from_minio(bucket_name: str, object_name: str):
    minio_client = get_minio_client()
    minio_client.remove_object(bucket_name=bucket_name, object_name=object_name)
