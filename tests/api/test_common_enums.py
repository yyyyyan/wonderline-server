from enum import Enum, auto

import pytest

from wonderline_app.api.common.enums import get_enum_names


@pytest.fixture
def mocked_enum_type():
    class MockEnum(Enum):
        createTime = auto()  # the value of the enum doesn't matter, so use auto()
        beginTime = auto()  # the value of the enum doesn't matter, so use auto()

    return MockEnum


def test_get_enum_names(mocked_enum_type):
    assert get_enum_names(mocked_enum_type) == ["createTime", "beginTime"]
