import datetime
import os

from cassandra.cqlengine.connection import setup


def connect_cassandra(function):
    def wrapper(*args, **kwargs):
        setup([os.environ['CASSANDRA_HOST']], os.environ['CASSANDRA_KEYSPACE'], retry_connect=True)
        return function(*args, **kwargs)

    return wrapper


def convert_string_date_to_timestamp(date: datetime.datetime) -> int:
    # date format: 2020-07-30 18:43:48.628000+0000
    timestamp = date.timestamp()  # 1596134528.628
    timestamp_without_point = int(str(timestamp).replace('.', ''))  # 1596134528628
    return timestamp_without_point
