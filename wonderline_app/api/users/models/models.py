"""
Definition of User related models.
"""
from flask_restplus import fields
from wonderline_app.api.namespaces import users_namespace

reduced_user_model = users_namespace.model("ReducedUser", {
    "id": fields.String(example="user_001"),
    "accessLevel": fields.String(example="everyone"),
    "name": fields.String(example="Jon Snow"),
    "avatarSrc": fields.String(example="https://wonderline-server/images/avatar.png"),
})

user_model = users_namespace.inherit("User", reduced_user_model, {
    "createTime": fields.Integer(example=1596134528628),
    "signature": fields.String(example="The king of the North, Danny is my QUEEN!"),
    "profileLqSrc": fields.String(example="http://wonderline-server/images/bkg.png"),
    "profileSrc": fields.String(example="http://wonderline-server/images/bkg.png"),
    "followerNb": fields.Integer(example=6),
    "followers": fields.List(fields.Nested(reduced_user_model))
})
