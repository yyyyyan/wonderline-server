"""
Implementations of users APIs' business logics.
"""
from wonderline_app.db.query import get_user_by_user_id


def get_user(user_id: str, followers_sort_type: str = "create_time", follower_nb: int = 6):
    # TODO: handle followers_sort_type and follower_nb
    user = get_user_by_user_id(user_id=user_id)
    # TODO: define a util function to wrap user with defined response pattern
    # Link: https://docs.google.com/document/d/1eNUO5M98UnZ8uOFdooFYX-e02mdg9p7nMOA-PLfknHQ/edit#heading=h.aq6ynq7k5no1
    return user
