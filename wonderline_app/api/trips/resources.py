from flask_restplus import Resource, Namespace

trips_namespace = Namespace('trips', description='Trips related APIs')


@trips_namespace.route("/trips/trip/<string:tripId>")
class Trip(Resource):
    def get(self, tripId):
        return "trip01"


@trips_namespace.route("/trips/trip/<string:tripId>/users")
class UsersByTrip(Resource):
    def get(self, tripId):
        return ["user01", "user02"]


@trips_namespace.route("/trips/trip/<string:tripId>/photos")
class PhotosByTrip(Resource):
    def get(self, tripId):
        return ["photo01", "photo02"]


@trips_namespace.route("/trips/trip/<string:tripId>/photos/<string:photoId>")
class Photo(Resource):
    def get(self, tripId, photoId):
        return "photo01"


@trips_namespace.route("/trips/trip/<string:tripId>/photos/<string:photoId>/comments")
class Comments(Resource):
    def get(self, tripId, photoId):
        return ["comment01", "comment02"]


@trips_namespace.route("/trips/trip/<string:tripId>/photos/<string:photoId>/comments/<string:commentId>/replies")
class Replies(Resource):
    def get(self, tripId, photoId, commentId):
        return ["reply01", "reply02"]
