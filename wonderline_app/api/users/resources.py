"""
Definitions of users APIs' resources.
"""
from flask import request
from flask_restplus import Resource

from wonderline_app.api.namespaces import users_namespace
from wonderline_app.api.users.business_logic import get_user
from wonderline_app.api.users.request_parsers import user_parser, user_albums_parser, followers_parser, \
    user_trips_parser, user_highlights_parser, user_mentions_parser
from wonderline_app.api.users.responses import user_res, user_albums_res, followers_res, user_trips_res, \
    user_highlights_res, user_mentions_res


@users_namespace.route("/<string:userId>")
class User(Resource):
    @users_namespace.expect(user_parser)
    @users_namespace.marshal_with(user_res)
    def get(self, userId):
        user_token = request.args.get("userToken")
        followers_sort_type = request.args.get("followersSortType")
        follower_nb = request.args.get("followerNb")
        return get_user(
            user_id=userId,
            followers_sort_type=followers_sort_type,
            follower_nb=follower_nb)


@users_namespace.route("/<string:userId>/followers")
class Followers(Resource):
    @users_namespace.expect(followers_parser)
    @users_namespace.marshal_with(followers_res)
    def get(self, userId):
        return 2


@users_namespace.route("/<string:userId>/trips")
class UserTrips(Resource):
    @users_namespace.expect(user_trips_parser)
    @users_namespace.marshal_with(user_trips_res)
    def get(self, userId):
        return ["trip01", "trip02"]


@users_namespace.route("/<string:userId>/highlights")
class UserHighlights(Resource):
    @users_namespace.expect(user_highlights_parser)
    @users_namespace.marshal_with(user_highlights_res)
    def get(self, userId):
        return ["highlight01", "highlight01"]


@users_namespace.route("/<string:userId>/albums")
class UserAlbums(Resource):
    @users_namespace.expect(user_albums_parser)
    @users_namespace.marshal_with(user_albums_res)
    def get(self, userId):
        return ["album01", "album02"]


@users_namespace.route("/<string:userId>/mentions")
class UserMentions(Resource):
    @users_namespace.expect(user_mentions_parser)
    @users_namespace.marshal_with(user_mentions_res)
    def get(self, userId):
        return ["mention01", "mention02"]
