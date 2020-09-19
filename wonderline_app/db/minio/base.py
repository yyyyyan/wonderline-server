import json
import logging
import os

from minio import ResponseError, Minio

LOGGER = logging.getLogger(__name__)

READ_ONLY_POLICY = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:GetBucketLocation",
                "Resource": "arn:aws:s3:::photos"
            },
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:ListBucket",
                "Resource": "arn:aws:s3:::photos"
            },
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::photos/*"
            }
        ]
    }
)


def create_minio_bucket(bucket_name: str, policy: str = READ_ONLY_POLICY, location: str = "us-east-1"):
    # TODO: config SSL connection (secure=False)
    #       see related Github issue https://github.com/minio/minio/issues/6820
    minio_client = get_minio_client()
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
