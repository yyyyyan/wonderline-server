"""
Flask application entrypoint.
"""
import logging
import os

from cassandra.cqlengine.connection import setup
from flask import Flask

from wonderline_app.api import rest_api
from wonderline_app.api.namespaces import users_namespace, trips_namespace, common_namespace
from wonderline_app.core.image_service import upload_image
from wonderline_app.db.minio.base import create_minio_bucket
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


def _setup_minio():
    create_minio_bucket(bucket_name=os.environ['MINIO_PHOTOS_BUCKET_NAME'])


APP = _create_app()
set_logging(logging_config_file_path=os.environ.get('CONFIG_FILE_PATH', 'config.yml'))
_setup_cassandra()
_setup_minio()


# TODO: remove this demo endpoint once the real API is finished
@APP.route('/upload_image_page', methods=['GET', 'POST'])
def upload_image_file():
    from flask import request
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'there is no image in the form!'
        image = request.files['image']
        return f"URLs: {upload_image(image)}"
    # when 'GET', return the html code
    return '''
    <h1>Upload new File</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="image">
      <input type="submit">
    </form>
    '''
