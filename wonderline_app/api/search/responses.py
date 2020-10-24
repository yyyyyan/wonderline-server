from flask_restplus import fields

from wonderline_app.api.common.responses import create_res
from wonderline_app.api.namespaces import search_namespace
from wonderline_app.api.users.response_models.models import reduced_user_model

search_users_response_model = create_res(
    namespace=search_namespace,
    name="SearchUsersResponse",
    payload_fields=fields.List(fields.Nested(reduced_user_model))
)
