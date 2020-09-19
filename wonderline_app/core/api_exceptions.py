from wonderline_app.core.response import Error


class APIError(Exception, Error):
    def __init__(self, message, code):
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)


class APIError404(APIError):
    def __init__(self, message):
        super().__init__(message=message, code=404)


class APIError401(APIError):
    def __init__(self, message):
        super().__init__(message=f"Unauthorized: {message}", code=401)


class APIError500(APIError):
    def __init__(self, exp_msg):
        super().__init__(message=f"Internal Server Error: {exp_msg}", code=500)
