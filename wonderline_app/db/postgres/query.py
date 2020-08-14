from wonderline_app.db.postgres.models import User
from wonderline_app.utils import convert_date_to_timestamp


def get_user_by_user_id(user_id: str):
    user = User.query.filter_by(id=user_id).one()
    user_dict = user.to_dict()
    user_dict['createTime'] = convert_date_to_timestamp(user_dict['createTime'])
    user_dict['followers'] = [
        User.query.filter_by(id=follower.to_id).one().to_dict()
        for follower in user.followers]
    return user_dict
