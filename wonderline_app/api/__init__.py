import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api

# Importing the following resources is essential to generate Swagger Document
from wonderline_app.api.users.resources import User, Followers, UserHighlights, UserAlbums, UserMentions, UserTrips, \
    UserSignup, UserSignIn, UserSignOut
from wonderline_app.api.trips.resources import Trip, TripUsers, TripPhotos, TripPhoto, PhotoComments, CommentReplies, \
    NewTrip
from wonderline_app.api.search.resources import SearchUser

rest_api = Api(version="v1.0a", title="Wondline APIs")
