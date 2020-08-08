"""
Definitions of users APIs' resources.
"""
from flask_restplus import Resource

from wonderline_app.api.namespaces import trips_namespace
from wonderline_app.api.trips.request_parsers import trip_parser, trip_users_parser, trip_photos_parser, \
    trip_photo_parser, photo_comments_parser, comment_replies_parser
from wonderline_app.api.trips.responses import trip_res, trip_users_res, trip_photos_res, trip_photo_res, \
    photo_comments_res, comment_replies_res


@trips_namespace.route("/trip/<string:tripId>")
class Trip(Resource):
    @trips_namespace.expect(trip_parser)
    @trips_namespace.marshal_with(trip_res)
    def get(self, tripId):
        return "trip01"


@trips_namespace.route("/trip/<string:tripId>/users")
class TripUsers(Resource):
    @trips_namespace.expect(trip_users_parser)
    @trips_namespace.marshal_with(trip_users_res)
    def get(self, tripId):
        return ["user01", "user02"]


@trips_namespace.route("/trip/<string:tripId>/photos")
class TripPhotos(Resource):
    @trips_namespace.expect(trip_photos_parser)
    @trips_namespace.marshal_with(trip_photos_res)
    def get(self, tripId):
        return ["photo01", "photo02"]


@trips_namespace.route("/trip/<string:tripId>/photos/<string:photoId>")
class TripPhoto(Resource):
    @trips_namespace.expect(trip_photo_parser)
    @trips_namespace.marshal_with(trip_photo_res)
    def get(self, tripId, photoId):
        return "photo01"


@trips_namespace.route("/trip/<string:tripId>/photos/<string:photoId>/comments")
class PhotoComments(Resource):
    @trips_namespace.expect(photo_comments_parser)
    @trips_namespace.marshal_with(photo_comments_res)
    def get(self, tripId, photoId):
        return ["comment01", "comment02"]


@trips_namespace.route("/trip/<string:tripId>/photos/<string:photoId>/comments/<string:commentId>/replies")
class CommentReplies(Resource):
    @trips_namespace.expect(comment_replies_parser)
    @trips_namespace.marshal_with(comment_replies_res)
    def get(self, tripId, photoId, commentId):
        return ["reply01", "reply02"]
