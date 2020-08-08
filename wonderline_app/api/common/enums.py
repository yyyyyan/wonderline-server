"""
Definition of common Enums used within API.
"""
from enum import Enum, auto


class AccessLevel(Enum):
    everyone = auto()


class Status(Enum):
    editing = auto()
    confirmed = auto()


class SortType(Enum):
    createTime = auto()  # the value of the enum doesn't matter, so use auto()


class FeedbackCode(Enum):
    success = auto()


class ErrorCode(Enum):
    serverError = auto()
    badRequest = auto()
    resourceNotFound = auto()


def get_enum_names(enum: Enum):
    return [name for name, _ in enum.__members__.items()]
