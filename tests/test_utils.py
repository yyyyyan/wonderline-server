from datetime import datetime

import pytest
from wonderline_app.utils import convert_date_to_timestamp_in_expected_unit, edit_distance, TimeUnit


@pytest.mark.parametrize(
    ("expected_time_unit", "expected_result"),
     [(TimeUnit.MILLISECOND, 1596134528628),
      (TimeUnit.SECOND, 1596134528)]
)
def test_convert_date_to_timestamp_in_expected_unit(expected_time_unit, expected_result):
    assert convert_date_to_timestamp_in_expected_unit(
        date=datetime.strptime("2020-07-30 18:42:08.628000+0000", "%Y-%m-%d %H:%M:%S.%f%z"),
        expected_unit=expected_time_unit
    ) == expected_result


@pytest.mark.parametrize(("word1", "word2", "expected_edit_dist"),
                         [("horse", "ros", 3),
                          ("intention", "execution", 5),
                          ("execution", "execution", 0)
                          ])
def test_edit_distance(word1, word2, expected_edit_dist):
    assert edit_distance(word1, word2) == expected_edit_dist
