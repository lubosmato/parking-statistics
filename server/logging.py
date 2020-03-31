import json
from pathlib import Path
import logging.config


def load_logger_config(log_config_file_name: str):
    log_config_path = str(Path(__file__).resolve().parent / log_config_file_name)
    with open(log_config_path, "r") as log_config_file:
        log_config = json.load(log_config_file)
        logging.config.dictConfig(log_config)
