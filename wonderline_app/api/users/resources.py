"""
Definitions of users APIs' resources.
"""
import logging

from flask import request
from flask_restplus import Resource

from wonderline_app.api.common.request_parsers import common_parser
from wonderline_app.api.namespaces import users_namespace
from wonderline_app.api.users.request_models.models import user_sign_up_model, user_sign_in_model, user_update_model
from wonderline_app.core.api_logics import get_user_complete_attributes, handle_request, get_user_followers, \
    get_albums_by_user, \
    get_trips_by_user, get_highlights_by_user, get_mentions_by_user, sign_up, sign_in, sign_out, update_user
from wonderline_app.api.users.request_parsers import user_parser, user_albums_parser, followers_parser, \
    user_trips_parser, user_highlights_parser, user_mentions_parser, user_sign_out_parser
from wonderline_app.api.users.responses import user_res, user_albums_res, followers_res, user_trips_res, \
    user_highlights_res, user_mentions_res, user_sign_up_res, user_sign_in_res, user_sign_out_res, reduced_user_res

LOGGER = logging.getLogger(__name__)


@users_namespace.route("/<string:userId>")
class User(Resource):
    @users_namespace.expect(user_parser)
    @users_namespace.marshal_with(user_res)
    def get(self, userId):
        args = user_parser.parse_args()
        user_token = args.get("userToken")
        followers_sort_type = args.get("followersSortType")
        follower_nb = args.get("followerNb")
        return handle_request(
            func=get_user_complete_attributes,
            user_token=user_token,
            user_id=userId,
            followers_sort_type=followers_sort_type,
            follower_nb=follower_nb)



@users_namespace.route("/<string:userId>/followers")
class Followers(Resource):
    @users_namespace.expect(followers_parser)
    @users_namespace.marshal_with(followers_res)
    def get(self, userId):
        args = followers_parser.parse_args()
        user_token = args.get("userToken")
        sort_type = args.get("sortType")
        nb = args.get("nb")
        start_index = args.get("startIndex")
        return handle_request(
            func=get_user_followers,
            user_id=userId,
            user_token=user_token,
            sort_type=sort_type,
            nb=nb,
            start_index=start_index)


@users_namespace.route("/<string:userId>/trips")
class UserTrips(Resource):
    @users_namespace.expect(user_trips_parser)
    @users_namespace.marshal_with(user_trips_res)
    def get(self, userId):
        args = user_trips_parser.parse_args()
        user_token = args.get("userToken")
        sort_type = args.get("sortType")
        nb = args.get("nb")
        start_index = args.get("startIndex")
        access_level = args.get("accessLevel")
        return handle_request(
            func=get_trips_by_user,
            user_token=user_token,
            user_id=userId,
            sort_type=sort_type,
            nb=nb,
            start_index=start_index,
            access_level=access_level
        )


@users_namespace.route("/<string:userId>/highlights")
class UserHighlights(Resource):
    @users_namespace.expect(user_highlights_parser)
    @users_namespace.marshal_with(user_highlights_res)
    def get(self, userId):
        args = user_highlights_parser.parse_args()
        user_token = args.get("userToken")
        sort_type = args.get("sortType")
        nb = args.get("nb")
        start_index = args.get("startIndex")
        access_level = args.get("accessLevel")
        return handle_request(
            func=get_highlights_by_user,
            user_token=user_token,
            user_id=userId,
            sort_type=sort_type,
            nb=nb,
            start_index=start_index,
            access_level=access_level
        )


@users_namespace.route("/<string:userId>/albums")
class UserAlbums(Resource):
    @users_namespace.expect(user_albums_parser)
    @users_namespace.marshal_with(user_albums_res)
    def get(self, userId):
        args = user_albums_parser.parse_args()
        user_token = args.get("userToken")
        sort_type = args.get("sortType")
        nb = args.get("nb")
        start_index = args.get("startIndex")
        access_level = args.get("accessLevel")
        return handle_request(
            func=get_albums_by_user,
            user_token=user_token,
            user_id=userId,
            sort_type=sort_type,
            nb=nb,
            start_index=start_index,
            access_level=access_level
        )


@users_namespace.route("/<string:userId>/mentions")
class UserMentions(Resource):
    @users_namespace.expect(user_mentions_parser)
    @users_namespace.marshal_with(user_mentions_res)
    def get(self, userId):
        args = user_mentions_parser.parse_args()
        user_token = args.get("userToken")
        sort_type = args.get("sortType")
        nb = args.get("nb")
        start_index = args.get("startIndex")
        access_level = args.get("accessLevel")
        return handle_request(
            func=get_mentions_by_user,
            user_token=user_token,
            user_id=userId,
            sort_type=sort_type,
            nb=nb,
            start_index=start_index,
            access_level=access_level
        )


@users_namespace.route("/signUp")
class UserSignup(Resource):
    @users_namespace.expect(user_sign_up_model, validate=True)
    @users_namespace.marshal_with(user_sign_up_res)
    def post(self):
        email = request.json["email"]
        user_unique_name = request.json["uniqueName"]
        password = request.json["password"]
        photo_data = request.json.get('photoData', None)
        return handle_request(
            func=sign_up,
            email=email,
            user_unique_name=user_unique_name,
            password=password,
            photo_data=photo_data
        )


@users_namespace.route("/signIn")
class UserSignIn(Resource):
    @users_namespace.expect(user_sign_in_model, validate=True)
    @users_namespace.marshal_with(user_sign_in_res)
    def post(self):
        email = request.json["email"]
        password = request.json["password"]
        return handle_request(
            func=sign_in,
            email=email,
            password=password,
        )


@users_namespace.route("/signOut")
class UserSignOut(Resource):
    @users_namespace.expect(user_sign_out_parser)
    @users_namespace.marshal_with(user_sign_out_res)
    def post(self):
        args = user_albums_parser.parse_args()
        user_token = args.get("userToken")
        return handle_request(
            func=sign_out,
            user_token=user_token
        )


@users_namespace.route("")
class UserUpdate(Resource):
    @users_namespace.expect(common_parser, user_update_model, validate=True)
    @users_namespace.marshal_with(reduced_user_res)
    def patch(self):
        args = user_albums_parser.parse_args()
        user_token = args.get("userToken")
        new_nick_name = request.json["nickName"]
        return handle_request(
            func=update_user,
            user_token=user_token,
            new_nick_name=new_nick_name
        )
