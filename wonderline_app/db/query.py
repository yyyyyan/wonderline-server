from .models import DBUser
from .utils import connect_cassandra


@connect_cassandra
def get_user_by_user_id(user_id: str):
    results = DBUser.objects(DBUser.user_id == user_id)
    if len(results):
        return results[0].json
    return None
