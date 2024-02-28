import json
import os
import tempfile

from src.helpers.helpers import write_to_file
from src.logger import SDVLogger

LOGGER = SDVLogger.get_logger("CONFIG_DC")


class OtaUpdServiceConfigProvider:
    CONFIG_NAME = "main_config.json"

    def __init__(self) -> None:
        self.source_conf = None
        self.config_path = None
        
    def init_config(self):
        crt_folder_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(crt_folder_path, OtaUpdServiceConfigProvider.CONFIG_NAME)
        f = open(config_path)
        self.source_conf = json.load(f)

        return self

    def set_topic_prefix(self, prefix: str):
        prefix = prefix.replace('/', '')
        new_send_sd = f"/{prefix}{self.source_conf['update_topic']}" 
        LOGGER.info(f"Set new topic for updater: '{new_send_sd}'")
        self.source_conf["update_topic"] = new_send_sd

        return self

    def generate(self, path_prefix=None):
        if path_prefix is None:
            path_prefix = tempfile.gettempdir()
        LOGGER.info(f"Generating new config file in folder '{path_prefix}'")

        if not os.path.exists(path_prefix):
            os.makedirs(path_prefix)
        config_path = os.path.join(path_prefix, OtaUpdServiceConfigProvider.CONFIG_NAME)

        with open(config_path, "w") as fp:
            json.dump(self.source_conf, fp)

        self.config_path = os.path.dirname(os.path.abspath(config_path))

        return self
