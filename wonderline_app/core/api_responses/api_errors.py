from http import HTTPStatus
from wonderline_app.core.api_responses.response import Error


class APIError(Exception, Error):
    def __init__(self, message, code):
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)


class APIError404(APIError):
    def __init__(self, message):
        super().__init__(message=message, code=HTTPStatus.NOT_FOUND.value)


class APIError401(APIError):
    def __init__(self, message):
        super().__init__(message=f"Unauthorized: {message}", code=HTTPStatus.UNAUTHORIZED.value)


class APIError500(APIError):
    def __init__(self, exp_msg):
        super().__init__(message=f"Internal Server Error: {exp_msg}", code=HTTPStatus.INTERNAL_SERVER_ERROR.value)


class APIError409(APIError):
    def __init__(self, exp_msg):
        super().__init__(message=f"Conflict: {exp_msg}", code=HTTPStatus.CONFLICT.value)
