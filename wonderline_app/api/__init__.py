from flask_restplus import Api

from wonderline_app.api.users.resources import User, Followers, UserHighlights, UserAlbums, UserMentions, UserTrips
from wonderline_app.api.trips.resources import Trip, TripUsers, TripPhotos, TripPhoto, PhotoComments, CommentReplies

rest_api = Api(version="v1.0a", title="Wondline APIs")
