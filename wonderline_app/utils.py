import datetime

import yaml
# Q:why importing logging.config:
# A: https://stackoverflow.com/questions/2234982/why-both-import-logging-and-import-logging-config-are-needed
import logging.config


def convert_date_to_timestamp(date: datetime.datetime):
    return date.timestamp() * 1000


def load_yaml_config(config_file_path):
    with open(config_file_path, 'r') as yml_file:
        cfg = yaml.load(yml_file, Loader=yaml.FullLoader)
    return cfg


def set_logging(logging_config_file_path):
    logging_config = load_yaml_config(config_file_path=logging_config_file_path)['logging']
    logging.config.dictConfig(logging_config)
