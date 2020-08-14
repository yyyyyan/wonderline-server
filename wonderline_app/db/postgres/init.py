import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    'postgresql://%s:%s@%s/%s' % (
        os.environ['POSTGRES_USER'],
        os.environ['POSTGRES_PASSWORD'],
        os.environ['POSTGRES_HOST'],
        os.environ['POSTGRES_DB']),
    convert_unicode=True,
    encoding='utf-8')

try:
    mymetadata = MetaData(bind=engine)
except Exception as e:
    print("debuggggg:", e)
# Base = declarative_base(metadata=mymetadata)
db_session = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine))
