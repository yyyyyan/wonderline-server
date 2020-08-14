"""
Flask application entrypoint.
"""
import logging
import os

from flask import Flask
from cassandra.cluster import Cluster
from minio import Minio
from minio.error import ResponseError

from wonderline_app.api import rest_api
from wonderline_app.api.namespaces import users_namespace, trips_namespace, common_namespace

LOGGER = logging.getLogger(__name__)
IS_DB_INITIALISED = False  # only for setup testing


def create_app():
    app = Flask(__name__)
    rest_api.add_namespace(common_namespace)
    rest_api.add_namespace(users_namespace)
    rest_api.add_namespace(trips_namespace)
    rest_api.init_app(app)
    return app


def connect_cassandra_and_return_session():
    """
    Connection object for Cassandra
    :return: session, cluster
    """
    cluster = Cluster([os.environ['CASSANDRA_HOST']], port=os.environ['CASSANDRA_PORT'])
    print("Ping Cassandra")
    session = cluster.connect()
    print("Cassandra connected")
    return session


def init_cassandra():
    def run_cql_script(file_path):
        with open(file_path, 'r') as f:
            commands = f.read().split(';')
            for command in commands:
                command = command.strip()
                if command != '':
                    print(f"Executing {command}")
                    session.execute(command)

    session = connect_cassandra_and_return_session()
    run_cql_script(file_path='DB_scripts/init_cassandra_tables_with_text_id.cql')
    session.set_keyspace('wonderline')
    run_cql_script(file_path='DB_scripts/init_cassandra_with_mock_data.cql')


def ping_minio():
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


APP = create_app()
# TODO: move global configuration(s) to another file
APP.config['BUNDLE_ERRORS'] = True  # Activate bundle error handling


@APP.route('/hello_world')
def hello_world():
    global IS_DB_INITIALISED
    if not IS_DB_INITIALISED:
        init_cassandra()
        IS_DB_INITIALISED = True
    ping_minio()
    return 'Hello, World!'
