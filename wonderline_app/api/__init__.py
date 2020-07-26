from flask_restplus import Api

from wonderline_app.api.users.resources import User, Followers, HighlightsByUser, AlbumsByUser, MentionsByUser, \
    TripsByUser
from wonderline_app.api.trips.resources import Trip, UsersByTrip, PhotosByTrip, Photo, Comments, Replies

rest_api = Api(version="v1.0a", title="Wondline APIs")
