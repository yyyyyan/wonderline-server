"""
Flask application entrypoint.
"""
import logging
import os
import secrets
from typing import Optional

from cassandra.cqlengine.connection import setup
from flask import Flask
from flask_login import LoginManager

from wonderline_app.api import rest_api
from wonderline_app.api.namespaces import users_namespace, trips_namespace, common_namespace, search_namespace
from wonderline_app.core.image_service import upload_encoded_image, upload_default_avatar_if_possible
from wonderline_app.db.minio.base import create_minio_bucket
from wonderline_app.db.postgres.models import User
from wonderline_app.utils import set_logging

LOGGER = logging.getLogger(__name__)


def _create_app():
    def __init_rest_api(app):
        rest_api.add_namespace(common_namespace)
        rest_api.add_namespace(search_namespace)
        rest_api.add_namespace(users_namespace)
        rest_api.add_namespace(trips_namespace)
        rest_api.init_app(app)

    def __setup_secret_key(app):
        app.secret_key = secrets.token_urlsafe(32)

    def __setup_login_manager(app):
        login_manager = LoginManager()
        login_manager.session_protection = 'strong'
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(user_id: str) -> Optional[User]:
            try:
                return User.get(user_id)
            except Exception:
                return None

    app = Flask(__name__)
    app.config.from_object('wonderline_app.flask_config.BaseConfig')
    __init_rest_api(app)
    __setup_secret_key(app)
    __setup_login_manager(app)

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
upload_default_avatar_if_possible()
