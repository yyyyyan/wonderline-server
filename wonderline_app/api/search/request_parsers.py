from wonderline_app.api.common.enums import get_enum_names, SearchSortType
from wonderline_app.api.common.request_parsers import common_parser

search_users_parser = common_parser.copy()

search_users_parser.add_argument(
    "query",
    type=str,
    location='args',
    required=True)
search_users_parser.add_argument(
    "sortType",
    type=str,
    choices=get_enum_names(SearchSortType),
    location='args',
    default=SearchSortType.BEST_MATCH.value)
search_users_parser.add_argument(
    "startIndex",
    type=int,
    location='args',
    default=0)
search_users_parser.add_argument(
    "nb",
    type=int,
    location='args',
    default=12)
