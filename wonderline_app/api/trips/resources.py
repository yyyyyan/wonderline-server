"""
Definitions of users APIs' resources.
"""
from flask import request
from flask_restplus import Resource

from wonderline_app.api.common.enums import SortType
from wonderline_app.api.common.request_parsers import common_parser
from wonderline_app.api.namespaces import trips_namespace
from wonderline_app.api.trips.request_models.models import trip_creation_model, trip_update_model
from wonderline_app.api.trips.request_parsers import trip_parser, trip_users_parser, trip_photos_parser, \
    trip_photo_parser, photo_comments_parser, comment_replies_parser
from wonderline_app.api.trips.responses import trip_res, trip_users_res, trip_photos_res, trip_photo_res, \
    photo_comments_res, comment_replies_res
from wonderline_app.core.api_logics import handle_request, get_complete_trip, get_users_by_trip, \
    get_photos_by_trip, get_photo_details, get_comments_by_photo, get_replies_by_comment, create_new_trip, update_trip


@trips_namespace.route("/<string:tripId>")
class Trip(Resource):
    @trips_namespace.expect(trip_parser)
    @trips_namespace.marshal_with(trip_res)
    def get(self, tripId):
        args = trip_parser.parse_args()
        user_token = args.get("userToken")
        users_sort_type = args.get("usersSortType")
        return handle_request(
            func=get_complete_trip,
            user_token=user_token,
            trip_id=tripId,
            users_sort_type=users_sort_type,
        )

    @trips_namespace.expect(common_parser, trip_update_model)
    @trips_namespace.marshal_with(trip_res)
    def patch(self, tripId):
        args = trip_parser.parse_args()
        user_token = args.get("userToken")
        name = request.json.get("name", None)
        description = request.json.get("description", None)
        user_ids = request.json.get("userIds", None)
        return handle_request(
            func=update_trip,
            user_token=user_token,
            trip_id=tripId,
            name=name,
            description=description,
            user_ids=user_ids,
        )


@trips_namespace.route("/<string:tripId>/users")
class TripUsers(Resource):
    @trips_namespace.expect(trip_users_parser)
    @trips_namespace.marshal_with(trip_users_res)
    def get(self, tripId):
        args = trip_users_parser.parse_args()
        user_token = args.get("userToken")
        sort_type = args.get("sortType")
        nb = args.get("nb")
        start_index = args.get("startIndex")
        return handle_request(
            func=get_users_by_trip,
            user_token=user_token,
            trip_id=tripId,
            sort_type=sort_type,
            nb=nb,
            start_index=start_index,
        )


@trips_namespace.route("/<string:tripId>/photos")
class TripPhotos(Resource):
    @trips_namespace.expect(trip_photos_parser)
    @trips_namespace.marshal_with(trip_photos_res)
    def get(self, tripId):
        args = trip_photos_parser.parse_args()
        user_token = args.get("userToken")
        sort_type = args.get("sortType")
        nb = args.get("nb")
        start_index = args.get("startIndex")
        access_level = args.get("accessLevel")
        return handle_request(
            func=get_photos_by_trip,
            user_token=user_token,
            trip_id=tripId,
            sort_type=sort_type,
            nb=nb,
            start_index=start_index,
            access_level=access_level
        )


@trips_namespace.route("/<string:tripId>/photos/<string:photoId>")
class TripPhoto(Resource):
    @trips_namespace.expect(trip_photo_parser)
    @trips_namespace.marshal_with(trip_photo_res)
    def get(self, tripId, photoId):
        args = trip_photo_parser.parse_args()
        user_token = args.get("userToken")
        liked_users_sort_type = args.get("likedUsersSortType")
        liked_user_nb = args.get("likedUserNb")
        comments_sort_type = args.get("commentsSortType")
        comment_nb = args.get("commentNb")
        return handle_request(
            func=get_photo_details,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            liked_users_sort_type=liked_users_sort_type,
            liked_user_nb=liked_user_nb,
            comments_sort_type=comments_sort_type,
            comment_nb=comment_nb
        )


@trips_namespace.route("/<string:tripId>/photos/<string:photoId>/comments")
class PhotoComments(Resource):
    @trips_namespace.expect(photo_comments_parser)
    @trips_namespace.marshal_with(photo_comments_res)
    def get(self, tripId, photoId):
        args = photo_comments_parser.parse_args()
        user_token = args.get("userToken")
        replies_sort_type = args.get("repliesSortType")
        reply_nb = args.get("replyNb")
        return handle_request(
            func=get_comments_by_photo,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            replies_sort_type=replies_sort_type,
            reply_nb=reply_nb
        )


@trips_namespace.route("/<string:tripId>/photos/<string:photoId>/comments/<string:commentId>/replies")
class CommentReplies(Resource):
    @trips_namespace.expect(comment_replies_parser)
    @trips_namespace.marshal_with(comment_replies_res)
    def get(self, tripId, photoId, commentId):
        args = comment_replies_parser.parse_args()
        user_token = args.get("userToken")
        sort_type = args.get("sortType")
        start_index = args.get("startIndex")
        nb = args.get("nb")
        return handle_request(
            func=get_replies_by_comment,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            comment_id=commentId,
            sort_type=sort_type,
            start_index=start_index,
            nb=nb
        )


@trips_namespace.route("/")
class NewTrip(Resource):
    @trips_namespace.expect(common_parser, trip_creation_model, validate=True)
    @trips_namespace.marshal_with(trip_res)
    def post(self):
        args = comment_replies_parser.parse_args()
        user_token = args.get("userToken")
        owner_id = request.json['ownerId']
        trip_name = request.json['tripName']
        user_ids = request.json.get('userIds', [])
        users_sort_type = request.json.get('usersSortType', SortType.CREATE_TIME.value)
        return handle_request(
            func=create_new_trip,
            user_token=user_token,
            owner_id=owner_id,
            trip_name=trip_name,
            user_ids=user_ids,
            users_sort_type=users_sort_type,
        )
