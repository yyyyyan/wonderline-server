"""
Definition of Trip related sub response_models.
"""
from flask_restplus import fields
from wonderline_app.api.namespaces import trips_namespace
from wonderline_app.api.users.response_models.models import reduced_user_model

reply_model = trips_namespace.model("Reply", {
    "id": fields.String(example="reply_001"),
    "user": fields.Nested(reduced_user_model),
    "createTime": fields.Integer(example=1596134528628),
    "content": fields.String(example="Hello World"),
    "likedNb": fields.Integer(example=3)
})

comment_model = trips_namespace.inherit("Comment", reply_model, {
    "replyNb": fields.Integer(example=1),
    "replies": fields.List(fields.Nested(reply_model))
})

reduced_photo_model = trips_namespace.model("ReducedPhoto", {
    "id": fields.String(example="user_001"),
    "accessLevel": fields.String(example="everyone"),
    "tripId": fields.String(example="trip_01"),
    "status": fields.String(example="confirmed"),
    "user": fields.Nested(reduced_user_model),
    "location": fields.String(example="The Wall"),
    "country": fields.String(example="House Stark"),
    "createTime": fields.Integer(example=1596134528628),
    "uploadTime": fields.Integer(example=1596134588628),
    "width": fields.Integer(example=1000),
    "height": fields.Integer(example=800),
    "lqSrc": fields.String(example="https://wonderline-server/images/photo.png"),
    "src": fields.String(example="https://wonderline-server/images/photo.png"),
    "likedNb": fields.Integer(example=200)
})

photo_model = trips_namespace.model("Photo", {
    "reducedPhoto": fields.Nested(reduced_photo_model),
    "hqSrc": fields.String(example="https://wonderline-server/images/photo.png"),
    "likedUsers": fields.List(fields.Nested(reduced_user_model)),
    "mentionedUsers": fields.List(fields.Nested(reduced_user_model)),
    "commentNb": fields.Integer(example=15),
    "comments": fields.List(fields.Nested(comment_model))
})
