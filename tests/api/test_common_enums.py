from wonderline_app.api.common.enums import get_enum_names, TripStatus


def test_get_enum_names():
    assert get_enum_names(TripStatus) == ["editing", "confirmed"]
