"""
Definitions of common API responses.
"""
from flask_restplus import fields

from wonderline_app.api.namespaces import common_namespace

feed_back_model = common_namespace.model("Feedback", {
    "code": fields.String(example="success"),
    "message": fields.String(example="Trip has been updated successfully.")
})

err_model = common_namespace.model("Error", {
    "code": fields.String(example="serverError"),
    "message": fields.String(example="Server Error, please try again.")
})

res_model = common_namespace.model("Response", {
    "feedbacks": fields.List(fields.Nested(feed_back_model, required=False)),
    "errors": fields.List(fields.Nested(err_model, required=False)),
    "timestamp": fields.Integer(example=1596925480790)
})


def create_res(namespace, name, payload_fields):
    return namespace.inherit(name, res_model, {
        "payload": payload_fields
    })
