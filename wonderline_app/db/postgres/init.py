import logging
import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

LOGGER = logging.getLogger(__name__)
engine = create_engine(
    'postgresql://%s:%s@%s/%s' % (
        os.environ.get('POSTGRES_USER'),
        os.environ.get('POSTGRES_PASSWORD'),
        os.environ.get('POSTGRES_HOST'),
        os.environ.get('POSTGRES_DB')),
    convert_unicode=True,
    encoding='utf-8')

try:
    postgres_meta_data = MetaData(bind=engine)
except Exception as e:
    LOGGER.exception("Fail to bind meta data:", e)
db_session = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine))
