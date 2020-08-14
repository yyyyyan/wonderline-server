from datetime import datetime

from wonderline_app.utils import convert_date_to_timestamp


class Response:
    def __init__(self, payload: dict):
        self.payload = payload
        self.errors = []
        self.feedbacks = []
        self.timestamp = None

    def add_error(self, err: str):
        self.errors.append(err)

    def add_feedback(self, feedback: str):
        self.feedbacks.append(feedback)

    @property
    def json(self):
        if self.timestamp is None:
            self.timestamp = convert_date_to_timestamp(datetime.now())
        return {
            "payload": self.payload,
            "errors": self.errors,
            "feedbacks": self.feedbacks,
            "timestamp": self.timestamp
        }
