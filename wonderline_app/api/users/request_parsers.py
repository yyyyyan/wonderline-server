"""
Definition of request parsers for User API.
"""
from wonderline_app.api.common.enums import get_enum_names, SortType, AccessLevel
from wonderline_app.api.common.request_parsers import common_parser

user_parser = common_parser.copy()
user_parser.add_argument(
    "followersSortType",
    type=str,
    choices=get_enum_names(SortType),
    default=SortType.createTime.name,
    help="Sort followers by followersSortType")
user_parser.add_argument(
    'followerNb',
    type=int,
    default=6,
    help="Number of returned followers")

followers_parser = common_parser.copy()
followers_parser.add_argument(
    "sortType",
    type=str,
    choices=get_enum_names(SortType),
    default=SortType.createTime.name)
followers_parser.add_argument(
    'startIndex',
    type=int,
    default=0)
followers_parser.add_argument(
    'nb',
    type=int,
    default=50)

# Similar structure as followers_parser
user_trips_parser = followers_parser.copy()
user_trips_parser.replace_argument("nb", default=3)
user_trips_parser.add_argument(
    "accessLevel",
    type=str,
    choices=get_enum_names(AccessLevel),
    default=AccessLevel.everyone.name)

# Same structure as user_trips_parser
user_highlights_parser = user_trips_parser.copy()

# Same structure as user_trips_parser
user_albums_parser = user_trips_parser.copy()

# Similar structure as user_trips_parser
user_mentions_parser = user_highlights_parser.copy()
user_mentions_parser.replace_argument('nb', default=12)


