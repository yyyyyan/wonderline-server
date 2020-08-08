"""
Definition of Trip API responses.
"""
from flask_restplus import fields

from wonderline_app.api.namespaces import trips_namespace
from wonderline_app.api.common.responses import create_res
from wonderline_app.api.trips.models.models import trip_model, reduced_photo_model
from wonderline_app.api.trips.models.sub_models import photo_model, comment_model, reply_model
from wonderline_app.api.users.models.models import reduced_user_model

trip_res = create_res(trips_namespace, "TripResponse",
                      fields.Nested(trip_model))

trip_users_res = create_res(trips_namespace, "TripUsersResponse",
                            fields.List(fields.Nested(reduced_user_model)))

trip_photos_res = create_res(trips_namespace, "TripPhotosResponse",
                             fields.List(fields.Nested(reduced_photo_model)))

trip_photo_res = create_res(trips_namespace, "TripPhotoResponse",
                            fields.Nested(photo_model))

photo_comments_res = create_res(trips_namespace, "PhotoCommentsResponse",
                                fields.List(fields.Nested(comment_model)))

comment_replies_res = create_res(trips_namespace, "CommentRepliesResponse",
                                 fields.List(fields.Nested(reply_model)))
