import datetime

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
