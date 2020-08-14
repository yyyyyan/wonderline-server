import datetime


def convert_date_to_timestamp(date: datetime.datetime) -> int:
    # date format: 2020-07-30 18:43:48.628000+0000
    timestamp = date.timestamp()  # 1596134528.628
    timestamp_without_point = int(str(timestamp).replace('.', ''))  # 1596134528628
    return timestamp_without_point
