"""
Implementations of users APIs' business logics.
"""
from wonderline_app.core.response import Response
from wonderline_app.db.postgres.query import get_user_by_user_id


def get_user(user_id: str, followers_sort_type: str = "create_time", follower_nb: int = 6):
    # TODO: handle followers_sort_type and follower_nb
    # TODO: handle errors
    user = get_user_by_user_id(user_id=user_id)
    return Response(payload=user)
