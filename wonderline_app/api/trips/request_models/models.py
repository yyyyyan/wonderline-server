import os

from flask_restplus import fields

from wonderline_app.api.namespaces import trips_namespace
from wonderline_app.utils import encode_image

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

# TODO: data example is too long
photo_original_data = trips_namespace.model("PhotoOriginalData", {
    "data": fields.String(required=True, example=encode_image(os.environ['TEST_PHOTO_PATH'])),
    "latitude": fields.String(example="64.752895", required=False, default=None),
    "latitudeRef": fields.String(example="N", required=False, default=None),
    "longitude": fields.String(example="14.53861166666667", required=False, default=None),
    "longitudeRef": fields.String(example="W", required=False, default=None),
    "location": fields.String(example="Shanghai", required=False, default=None),
    "time": fields.Integer(example=1605306885, required=True),  # original image upload time
    "width": fields.Integer(example=400, required=True),  # it may be optional
    "height": fields.Integer(example=600, required=True),  # it may be optional
    "mentionedUserIds": fields.List(fields.String(example="user_001"), required=False),
    "accessLevel": fields.String(example="everyone", required=True)
})

photo_upload_model = trips_namespace.model("OriginalPhotos", {
    "originalPhotos": fields.List(fields.Nested(photo_original_data), required=True)
})

photo_update_model = trips_namespace.model("PhotoToUpdate", {
    "accessLevel": fields.String(example="everyone", required=False, default=None),
    "mentionedUserIds": fields.List(fields.String(example="user_001", required=False, default=None)),
    "location": fields.String(example="Shanghai", required=False, default=None)
})
photos_update_model = trips_namespace.model("PhotosToUpdate", {
    "photoIds": fields.List(fields.String(example="photo_01_1", required=True)),
    "accessLevel": fields.String(example="everyone", required=False, default=None),
})
photos_delete_model = trips_namespace.model("PhotosToDelete", {
    "photoIds": fields.List(fields.String(example="photo_01_1", required=True))
})
