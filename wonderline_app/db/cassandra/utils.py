import os

from cassandra.cqlengine.connection import setup


def connect_cassandra(function):
    def wrapper(*args, **kwargs):
        setup([os.environ['CASSANDRA_HOST']], os.environ['CASSANDRA_KEYSPACE'], retry_connect=True)
        return function(*args, **kwargs)

    return wrapper
