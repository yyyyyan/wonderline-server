"""
Definitions of users APIs' resources.
"""
from flask import request
from flask_restplus import Resource

from wonderline_app.api.common.enums import SortType
from wonderline_app.api.common.request_parsers import common_parser
from wonderline_app.api.common.responses import res_model
from wonderline_app.api.namespaces import trips_namespace
from wonderline_app.api.trips.request_models.models import trip_creation_model, trip_update_model, photo_upload_model, \
    photo_update_model, photos_delete_model, photos_update_model, original_comment_model, comment_update_model
from wonderline_app.api.trips.request_parsers import trip_parser, trip_users_parser, trip_photos_parser, \
    trip_photo_parser, photo_comments_parser, comment_replies_parser
from wonderline_app.api.trips.responses import trip_res, trip_users_res, trip_photos_res, trip_photo_res, \
    photo_comments_res, comment_replies_res, comment_res, reply_res
from wonderline_app.core.api_logics import handle_request, get_complete_trip, get_users_by_trip, \
    get_photos_by_trip, get_photo_details, get_comments_by_photo, get_replies_by_comment, create_new_trip, update_trip, \
    upload_trip_photos, update_trip_photo, delete_trip_photos, update_trip_photos, create_new_reply, create_new_comment, \
    update_comment, delete_comment, delete_reply, update_reply


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

    @trips_namespace.expect(common_parser, trip_update_model, validate=True)
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

    @trips_namespace.expect(common_parser, photo_upload_model, validate=True)
    @trips_namespace.marshal_with(trip_photos_res)
    def post(self, tripId):
        args = common_parser.parse_args()
        user_token = args.get('userToken')
        original_photos = request.json['originalPhotos']

        return handle_request(
            func=upload_trip_photos,
            user_token=user_token,
            trip_id=tripId,
            original_photos=original_photos
        )

    @trips_namespace.expect(common_parser, photos_delete_model, validate=True)
    @trips_namespace.marshal_with(res_model)
    def delete(self, tripId):
        args = common_parser.parse_args()
        user_token = args.get('userToken')
        photo_ids = request.json['photoIds']
        return handle_request(
            func=delete_trip_photos,
            user_token=user_token,
            trip_id=tripId,
            photo_ids=photo_ids
        )

    @trips_namespace.expect(common_parser, photos_update_model, validate=True)
    @trips_namespace.marshal_with(trip_photos_res)
    def patch(self, tripId):
        args = trip_photo_parser.parse_args()
        user_token = args.get("userToken")
        photo_ids = request.json['photoIds']
        access_level = request.json.get('accessLevel', None)
        return handle_request(
            func=update_trip_photos,
            user_token=user_token,
            trip_id=tripId,
            photo_ids=photo_ids,
            access_level=access_level,
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

    @trips_namespace.expect(common_parser, photo_update_model, validate=True)
    @trips_namespace.marshal_with(trip_photo_res)
    def patch(self, tripId, photoId):
        args = trip_photo_parser.parse_args()
        user_token = args.get("userToken")
        access_level = request.json.get('accessLevel', None)
        mentioned_users = request.json.get('mentionedUserIds', None)
        location = request.json.get('location', None)
        is_liked = request.json.get('isLiked', None)
        return handle_request(
            func=update_trip_photo,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            access_level=access_level,
            mentioned_users=mentioned_users,
            location=location,
            is_liked=is_liked,
        )


@trips_namespace.route("/<string:tripId>/photos/<string:photoId>/comments")
class PhotoComments(Resource):
    @trips_namespace.expect(photo_comments_parser)
    @trips_namespace.marshal_with(photo_comments_res)
    def get(self, tripId, photoId):
        args = photo_comments_parser.parse_args()
        user_token = args.get("userToken")
        comments_sort_type = args.get("commentsSortType")
        nb = args.get("nb")
        start_index = args.get("startIndex")
        replies_sort_type = args.get("repliesSortType")
        reply_nb = args.get("replyNb")
        return handle_request(
            func=get_comments_by_photo,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            comments_sort_type=comments_sort_type,
            nb=nb,
            start_index=start_index,
            replies_sort_type=replies_sort_type,
            reply_nb=reply_nb
        )

    @trips_namespace.expect(common_parser, photo_comments_parser, original_comment_model, validate=True)
    @trips_namespace.marshal_with(photo_comments_res)
    def post(self, tripId, photoId):
        args = photo_comments_parser.parse_args()
        user_token = args.get("userToken")
        comments_sort_type = args.get("commentsSortType")
        nb = args.get("nb")
        start_index = args.get("startIndex")
        replies_sort_type = args.get("repliesSortType")
        reply_nb = args.get("replyNb")
        comment = request.json['comment']
        return handle_request(
            func=create_new_comment,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            comments_sort_type=comments_sort_type,
            nb=nb,
            start_index=start_index,
            replies_sort_type=replies_sort_type,
            reply_nb=reply_nb,
            comment=comment,
        )


@trips_namespace.route("/<string:tripId>/photos/<string:photoId>/comments/<string:commentId>")
class PhotoComment(Resource):
    @trips_namespace.expect(common_parser, comment_update_model, validate=True)
    @trips_namespace.marshal_with(comment_res)
    def patch(self, tripId, photoId, commentId):
        args = comment_replies_parser.parse_args()
        user_token = args.get("userToken")
        is_like = request.json['isLike']
        return handle_request(
            func=update_comment,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            comment_id=commentId,
            is_like=is_like,
        )

    @trips_namespace.expect(common_parser, validate=True)
    @trips_namespace.marshal_with(res_model)
    def delete(self, tripId, photoId, commentId):
        args = comment_replies_parser.parse_args()
        user_token = args.get("userToken")
        return handle_request(
            func=delete_comment,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            comment_id=commentId,
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

    @trips_namespace.expect(common_parser, comment_replies_parser, original_comment_model, validate=True)
    @trips_namespace.marshal_with(comment_replies_res)
    def post(self, tripId, photoId, commentId):
        args = comment_replies_parser.parse_args()
        user_token = args.get("userToken")
        sort_type = args.get("sortType")
        start_index = args.get("startIndex")
        nb = args.get("nb")
        reply = request.json['comment']
        return handle_request(
            func=create_new_reply,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            comment_id=commentId,
            reply=reply,
            sort_type=sort_type,
            start_index=start_index,
            nb=nb
        )


@trips_namespace.route("/<string:tripId>/photos/<string:photoId>/comments/<string:commentId>/replies/<string:replyId>")
class CommentReply(Resource):
    @trips_namespace.expect(common_parser, validate=True)
    @trips_namespace.marshal_with(res_model)
    def delete(self, tripId, photoId, commentId, replyId):
        args = comment_replies_parser.parse_args()
        user_token = args.get("userToken")
        return handle_request(
            func=delete_reply,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            comment_id=commentId,
            reply_id=replyId,
        )

    @trips_namespace.expect(common_parser, comment_update_model, validate=True)
    @trips_namespace.marshal_with(reply_res)
    def patch(self, tripId, photoId, commentId, replyId):
        args = comment_replies_parser.parse_args()
        user_token = args.get("userToken")
        is_like = request.json['isLike']
        return handle_request(
            func=update_reply,
            user_token=user_token,
            trip_id=tripId,
            photo_id=photoId,
            comment_id=commentId,
            reply_id=replyId,
            is_like=is_like
        )


@trips_namespace.route("/")
class NewTrip(Resource):
    @trips_namespace.expect(common_parser, trip_creation_model, validate=True)
    @trips_namespace.marshal_with(trip_res)
    def post(self):
        args = common_parser.parse_args()
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
