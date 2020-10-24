"""
Definition of common Enums used within API.
"""
from enum import Enum, auto


class ExplicitEnum(Enum):
    """
    Enum with more explicit error message for missing values.
    """

    @classmethod
    def _missing_(cls, value):
        raise ValueError(
            "%r is not a valid %s, please select one of %s"
            % (value, cls.__name__, str(list(cls._value2member_map_.keys())))
        )


class AccessLevel(ExplicitEnum):
    EVERYONE = 'everyone'


class TripStatus(ExplicitEnum):
    EDITING = 'editing'
    CONFIRMED = 'confirmed'


class SortType(ExplicitEnum):
    CREATE_TIME = 'createTime'


class SearchSortType(ExplicitEnum):
    BEST_MATCH = 'bestMatch'


def get_enum_names(enum: Enum):
    return [item.value for _, item in enum.__members__.items()]
