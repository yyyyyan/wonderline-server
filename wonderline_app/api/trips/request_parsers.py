"""
Definition of request parsers for Trip API.
"""
from wonderline_app.api.common.enums import get_enum_names, SortType, AccessLevel
from wonderline_app.api.common.request_parsers import common_parser

trip_parser = common_parser.copy()
trip_parser.add_argument(
    "usersSortType",
    type=str,
    choices=get_enum_names(SortType),
    location='args',
    default=SortType.createTime.name)
trip_parser.add_argument(
    'userNb',
    type=int,
    location='args',
    default=6)

trip_users_parser = common_parser.copy()
trip_users_parser.add_argument(
    "sortType",
    type=str,
    choices=get_enum_names(SortType),
    location='args',
    default=SortType.createTime.name)
trip_users_parser.add_argument(
    'startIndex',
    type=int,
    location='args',
    default=0)
trip_users_parser.add_argument(
    'nb',
    type=int,
    location='args',
    default=50)

# Similar structure as trip_users_parser
trip_photos_parser = trip_users_parser.copy()
trip_photos_parser.replace_argument(
    'nb',
    type=int,
    location='args',
    default=3)
trip_photos_parser.add_argument(
    "accessLevel",
    type=str,
    choices=get_enum_names(AccessLevel),
    location='args',
    default=AccessLevel.everyone.name)

trip_photo_parser = common_parser.copy()
trip_photo_parser.add_argument(
    "likedUsersSortType",
    type=str,
    choices=get_enum_names(SortType),
    location='args',
    default=SortType.createTime.name)
trip_photo_parser.add_argument(
    'likedUserNb',
    type=int,
    location='args',
    default=6)
trip_photo_parser.add_argument(
    "commentsSortType",
    type=str,
    choices=get_enum_names(SortType),
    location='args',
    default=SortType.createTime.name)
trip_photo_parser.add_argument(
    'commentNb',
    type=int,
    location='args',
    default=6)

photo_comments_parser = common_parser.copy()
photo_comments_parser.add_argument(
    "repliesSortType",
    type=str,
    choices=get_enum_names(SortType),
    location='args',
    default=SortType.createTime.name)
photo_comments_parser.add_argument(
    'replyNb',
    type=int,
    location='args',
    default=6)

comment_replies_parser = common_parser.copy()
comment_replies_parser.add_argument(
    "sortType",
    type=str,
    choices=get_enum_names(SortType),
    location='args',
    default=SortType.createTime.name)
comment_replies_parser.add_argument(
    'startIndex',
    type=int,
    location='args',
    default=0)
comment_replies_parser.add_argument(
    'nb',
    type=int,
    location='args',
    default=6)
