"""
Definition of User API responses.
"""
from flask_restplus import fields

from wonderline_app.api.namespaces import users_namespace
from wonderline_app.api.common.responses import create_res
from wonderline_app.api.trips.models.models import reduced_trip_model
from wonderline_app.api.users.models.models import user_model, reduced_user_model
from wonderline_app.api.users.models.sub_models import reduced_album_model, reduced_highlight_model, mention_model

user_res = create_res(users_namespace, "UserResponse", fields.Nested(user_model))

followers_res = create_res(users_namespace, "FollowerResponse",
                           fields.List(fields.Nested(reduced_user_model)))

user_trips_res = create_res(users_namespace, "UserTripsResponse",
                            fields.List(fields.Nested(reduced_trip_model)))

user_highlights_res = create_res(users_namespace, "UserHighlightsResponse",
                                 fields.List(fields.Nested(reduced_highlight_model)))

user_albums_res = create_res(users_namespace, "UserAlbumsResponse",
                             fields.List(fields.Nested(reduced_album_model)))

user_mentions_res = create_res(users_namespace, "UserMentionsResponse",
                               fields.List(fields.Nested(mention_model)))
