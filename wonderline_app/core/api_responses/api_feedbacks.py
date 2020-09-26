from http import HTTPStatus

from wonderline_app.core.api_responses.response import Feedback


class APIFeedback201(Feedback):
    def __init__(self, message):
        super().__init__(message=message, code=HTTPStatus.CREATED.value)
