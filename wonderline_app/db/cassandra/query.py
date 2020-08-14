"""
Implementations of cassandra database query.
"""
from typing import Optional

from wonderline_app.db.cassandra.models import Trip
from wonderline_app.db.cassandra.utils import connect_cassandra


@connect_cassandra
def get_trip_by_trip_id(trip_id: str) -> Optional[Trip]:
    results = Trip.objects(Trip.trip_id == trip_id)
    if len(results):
        return results[0]
    return None
