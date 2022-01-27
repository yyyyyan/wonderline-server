"""
Definition of User related response_models.
"""
from flask_restplus import fields
from wonderline_app.api.namespaces import users_namespace

user_token_model = users_namespace.model("UserToken", {
    "userToken": fields.String()
})

reduced_user_model = users_namespace.model("ReducedUser", {
    "id": fields.String(example="user_001"),
    "accessLevel": fields.String(example="everyone"),
    "nickName": fields.String(example="Jon Snow"),
    "uniqueName": fields.String(example="jon_snow"),
    "avatarSrc": fields.String(example="https://wonderline-server/images/avatar.png"),
})

user_model = users_namespace.model("User", {
    "reducedUser": fields.Nested(reduced_user_model, allow_null=True),
    "createTime": fields.Integer(example=1596134528628),
    "signature": fields.String(example="The king of the North, Danny is my QUEEN!"),
    "profileLqSrc": fields.String(example="http://wonderline-server/images/bkg.png"),
    "profileSrc": fields.String(example="http://wonderline-server/images/bkg.png"),
    "followerNb": fields.Integer(example=6),
    "followers": fields.List(fields.Nested(reduced_user_model)),
    "isFollowedByLoginUser": fields.Boolean(example=False)
})

sign_in_user_model = users_namespace.model("SignUser", {
    "userToken": fields.String(),
    "user": fields.Nested(user_model)
})

