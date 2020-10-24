from flask_restplus import fields

from wonderline_app.api.namespaces import trips_namespace

trip_creation_model = trips_namespace.model("TripCreationModel", {
    "ownerId": fields.String(example="user_001", required=True),
    "tripName": fields.String(example="New Trip Name", required=False),
    "userIds": fields.List(fields.String(example='user_001', required=False)),
    "usersSortType": fields.String(example="createTime", required=False),
})

trip_update_model = trips_namespace.model("TripUpdateModel", {
    "name": fields.String(example="New Trip Name", required=False),
    "description": fields.String(example="New Trip Description", required=False),
    "userIds": fields.List(fields.String(example='user_001', required=False))
})
