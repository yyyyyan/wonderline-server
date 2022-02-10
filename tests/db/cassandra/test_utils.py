import pytest

from wonderline_app.db.cassandra.utils import convert_sort_by


@pytest.mark.parametrize(
    "sort_by,expected",
    [
        ("createTime", ["create_time"]),  # normal case
        ("-createTime", ["-create_time"]),  # with minus
        (["createTime", "like_nb"], ["create_time", "like_nb"]),  # with list
        (["createTime", "-like_nb"], ["create_time", "-like_nb"]),  # with list and minus
        (["-xx", "yy"], ["-xx", "yy"])  # other sort by not present in the map
     ],
)
def test_convert_sort_by(sort_by, expected):
    assert convert_sort_by(sort_by) == expected
