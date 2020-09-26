from datetime import datetime
from typing import Dict

from wonderline_app.utils import convert_date_to_timestamp


class CodeMessage:
    def __init__(self, code: int = None, message: str = None):
        self.code = code
        self.message = message

    @property
    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message
        }

    def __str__(self):
        return repr(self.message)


class Error(CodeMessage):
    def __init__(self, code: int = None, message: str = None):
        super().__init__(code, message)


class Feedback(CodeMessage):
    def __init__(self, code: int = None, message: str = None):
        super().__init__(code, message)


class Response:
    def __init__(self, payload: dict = None, errors=None, feedback=None):
        self.payload = payload if payload else {}
        self.errors = errors if errors else []
        self.feedbacks = feedback if feedback else []
        self.timestamp = None

    @property
    def has_errors(self):
        return len(self.errors) > 0

    @property
    def has_feedbacks(self):
        return len(self.feedbacks) > 0

    def add_error(self, err: Error):
        self.errors.append(err)

    def add_feedback(self, feedback: Feedback):
        self.feedbacks.append(feedback)

    def to_dict(self) -> Dict:
        if self.timestamp is None:
            self.timestamp = convert_date_to_timestamp(datetime.now())
        return {
            "payload": self.payload,
            "errors": [err.to_dict for err in self.errors],
            "feedbacks": [fb.to_dict for fb in self.feedbacks],
            "timestamp": self.timestamp
        }
