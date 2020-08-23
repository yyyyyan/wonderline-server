"""
Flask application entrypoint.
"""
import logging
import os

from cassandra.cqlengine.connection import setup
from flask import Flask
from minio import Minio
from minio.error import ResponseError

from wonderline_app.api import rest_api
from wonderline_app.api.namespaces import users_namespace, trips_namespace, common_namespace
from wonderline_app.utils import set_logging

LOGGER = logging.getLogger(__name__)


def _create_app():
    app = Flask(__name__)
    app.config.from_object('wonderline_app.flask_config.BaseConfig')
    rest_api.add_namespace(common_namespace)
    rest_api.add_namespace(users_namespace)
    rest_api.add_namespace(trips_namespace)
    rest_api.init_app(app)
    return app


def _setup_cassandra():
    setup(
        hosts=[os.environ.get('CASSANDRA_HOST')],
        default_keyspace=os.environ.get('CASSANDRA_KEYSPACE'),
        retry_connect=True,
        lazy_connect=True)


def _ping_minio():
    print("Ping minio")
    # TODO: config SSL connection (secure=False)
    #       see related Github issue https://github.com/minio/minio/issues/6820
    minio_client = Minio(os.environ['MINIO_HOST'] + ':' + os.environ['MINIO_PORT'],
                         access_key=os.environ['MINIO_ACCESS_KEY'],
                         secret_key=os.environ['MINIO_SECRET_KEY'],
                         secure=False)
    # Make a bucket with the make_bucket API call.
    try:
        bucket_name = "mybucket"
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name, location="us-east-1")
            print(f"Minio bucket {bucket_name} created")
        else:
            print(f"Minio bucket {bucket_name} already exists")
    except ResponseError as err:
        print(err)


APP = _create_app()
set_logging(logging_config_file_path=os.environ.get('CONFIG_FILE_PATH', 'config.yml'))
_setup_cassandra()


@APP.route('/ping_minio')
def ping_minio():
    _ping_minio()
    return 'Ping minio: success'
