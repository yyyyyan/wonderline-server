"""
Definition of User related sub models.
"""
from flask_restplus import fields
from wonderline_app.api.namespaces import users_namespace
from wonderline_app.api.trips.models.sub_models import reduced_photo_model

reduced_highlight_model = users_namespace.model("ReducedHighlight", {
    "id": fields.String(example="highlight_001"),
    "accessLevel": fields.String(example="everyone"),
    "coverPhoto": fields.Nested(reduced_photo_model),
    "description": fields.String(example="Joined the Night's Watch"),
    "createTime": fields.Integer(example=1596134528628)
})

rearranged_photo_model = users_namespace.model("RearrangedPhoto", {
    "photo": fields.Nested(reduced_photo_model),
    "ratioType": fields.String(example="square")
})

reduced_album_model = users_namespace.model("ReducedAlbum", {
    "id": fields.String(example="album_001"),
    "accessLevel": fields.String(example="everyone"),
    "coverPhotos": fields.List(fields.Nested(rearranged_photo_model)),
    "createTime": fields.Integer(example=1596134528628)
})

mention_model = users_namespace.model("Mention", {
    "id": fields.String(example="mention_001"),
    "photo": fields.Nested(reduced_photo_model),
    "accessLevel": fields.String(example="everyone")
})
