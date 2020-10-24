from flask_restplus import Resource

from wonderline_app.api.namespaces import search_namespace
from wonderline_app.api.search.request_parsers import search_users_parser
from wonderline_app.api.search.responses import search_users_response_model
from wonderline_app.core.api_logics import handle_request, search_users


@search_namespace.route("/users")
class SearchUser(Resource):
    @search_namespace.expect(search_users_parser, validate=True)
    @search_namespace.marshal_with(search_users_response_model)
    def get(self):
        args = search_users_parser.parse_args()
        user_token = args.get("userToken")
        query = args.get("query")
        start_index = args.get("startIndex")
        nb = args.get("nb")
        users_sort_type = args.get("sortType")
        return handle_request(
            func=search_users,
            user_token=user_token,
            query=query,
            users_sort_type=users_sort_type,
            start_index=start_index,
            nb=nb
        )
