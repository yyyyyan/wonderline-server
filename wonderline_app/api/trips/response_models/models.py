"""
Definition of Trip related response_models.
"""
from flask_restplus import fields
from wonderline_app.api.namespaces import trips_namespace
from wonderline_app.api.users.response_models.models import reduced_user_model
from wonderline_app.api.trips.response_models.sub_models import reduced_photo_model

reduced_trip_model = trips_namespace.model("ReducedTrip", {
    "id": fields.String(example="trip_01"),
    "accessLevel": fields.String(example="everyone"),
    "status": fields.String(example="confirmed"),
    "name": fields.String(example="Winter is here"),
    "description": fields.String(example="Westeros shall suffer from death"),
    "users": fields.List(fields.Nested(reduced_user_model)),
    "createTime": fields.Integer(example=1596134528628),
    "beginTime": fields.Integer(example=1596134628628),
    "endTime": fields.Integer(example=1596135628628),
    "photoNb": fields.Integer(example=9),
    "coverPhoto": fields.Nested(reduced_photo_model)
})

trip_model = trips_namespace.model("Trip", {
    "reducedTrip": fields.Nested(reduced_trip_model),
    "likedNb": fields.Integer(example=200),
    "sharedNb": fields.Integer(example=56),
    "savedNb": fields.Integer(example=120)
})