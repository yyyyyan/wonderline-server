from datetime import datetime

import pytest
from wonderline_app.utils import convert_date_to_timestamp_in_ms_unit, edit_distance


def test_convert_string_date_to_timestamp():
    assert convert_date_to_timestamp_in_ms_unit(
        datetime.strptime("2020-07-30 18:42:08.628000+0000", "%Y-%m-%d %H:%M:%S.%f%z")) == 1596134528628


@pytest.mark.parametrize(("word1", "word2", "expected_edit_dist"),
                         [("horse", "ros", 3),
                          ("intention", "execution", 5),
                          ("execution", "execution", 0)
                          ])
def test_edit_distance(word1, word2, expected_edit_dist):
    assert edit_distance(word1, word2) == expected_edit_dist
