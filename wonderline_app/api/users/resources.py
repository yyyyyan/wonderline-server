from flask_restplus import Resource, Namespace

from wonderline_app.db.query import get_user_by_user_id

users_namespace = Namespace('users', description='Users related APIs')


@users_namespace.route("/user/<string:userId>")
class User(Resource):
    def get(self, userId):
        # TODO: followersSortType, followerNb
        return get_user_by_user_id(user_id=userId)


@users_namespace.route("/users/<string:userId>/followers")
class Followers(Resource):
    def get(self, userId):
        return 2


@users_namespace.route("/users/<string:userId>/trips")
class TripsByUser(Resource):
    def get(self, userId):
        return ["trip01", "trip02"]


@users_namespace.route("/users/<string:userId>/highlights")
class HighlightsByUser(Resource):
    def get(self, userId):
        return ["highlight01", "highlight01"]


@users_namespace.route("/users/<string:userId>/albums")
class AlbumsByUser(Resource):
    def get(self, userId):
        return ["album01", "album02"]


@users_namespace.route("/users/<string:userId>/mentions")
class MentionsByUser(Resource):
    def get(self, userId):
        return ["mention01", "mention02"]
