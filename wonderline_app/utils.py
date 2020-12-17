import base64
import datetime
import uuid

import reverse_geocoder
import yaml
# Q:why importing logging.config:
# A: https://stackoverflow.com/questions/2234982/why-both-import-logging-and-import-logging-config-are-needed
import logging.config


def convert_date_to_timestamp_in_ms_unit(date: datetime.datetime):
    return date.timestamp() * 1000


def load_yaml_config(config_file_path):
    with open(config_file_path, 'r') as yml_file:
        cfg = yaml.load(yml_file, Loader=yaml.FullLoader)
    return cfg


def set_logging(logging_config_file_path):
    logging_config = load_yaml_config(config_file_path=logging_config_file_path)['logging']
    logging.config.dictConfig(logging_config)


def edit_distance(word1: str, word2: str) -> int:
    l1, l2 = len(word1), len(word2)
    dp = [[0] * (l2 + 1) for _ in range(l1 + 1)]
    for i in range(l1 + 1):
        dp[i][0] = i
    for i in range(l2 + 1):
        dp[0][i] = i
    for i in range(1, l1 + 1):
        for j in range(1, l2 + 1):
            # insert on word1
            insert = 1 + dp[i][j - 1]
            # delete on word1
            delete = 1 + dp[i - 1][j]
            # replace on word1, word2
            replace = 1 + dp[i - 1][j - 1]
            if word1[i - 1] == word2[j - 1]:
                replace -= 1
            dp[i][j] = min(insert, delete, replace)
    return dp[l1][l2]


def get_utc_with_delta(delta: int):
    current_time_utc = datetime.datetime.now()
    current_time_utc_plus_delta = current_time_utc + datetime.timedelta(hours=delta)
    return current_time_utc_plus_delta


def get_current_timestamp():
    return get_utc_with_delta(delta=0).timestamp()


def construct_location(longitude, latitude, latitude_ref='N', longitude_ref='W'):
    if longitude is None or latitude is None:
        return None
    return longitude + ' ' + longitude_ref + ', ' + latitude + ' ' + latitude_ref


def infer_country_from_location(longitude: float, latitude: float):
    if longitude is None or latitude is None:
        return ''
    results = reverse_geocoder.search((latitude, longitude))  # default mode = 2
    if results is not None and len(results):
        res = results[0]
        location = res['name']
        country = res['cc']
        return location + ', ' + country
    return ''


def get_uuid() -> str:
    return str(uuid.uuid1())


def encode_image(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode("utf-8")  # use decode to convert bytes to string
