from datetime import datetime

from wonderline_app.db.utils import convert_string_date_to_timestamp


def test_convert_string_date_to_timestamp():
    assert convert_string_date_to_timestamp(
        datetime.strptime("2020-07-30 18:42:08.628000+0000", "%Y-%m-%d %H:%M:%S.%f%z")) == 1596134528628
