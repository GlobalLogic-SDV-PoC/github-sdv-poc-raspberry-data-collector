import json
import os
import tempfile

from src.helpers.helpers import write_to_file
from src.logger import SDVLogger

LOGGER = SDVLogger.get_logger("CONFIG_DC")


class DCServiceConfigProvider:
    CONFIG_NAME = "main_config.json"

    def __init__(self) -> None:
        self.source_conf = None
        self.config_path = None
        self.ram_path = None
        self.temp_path = None
        self.storage_path = None
        self.expected_temp_value = None
        self.expected_storage_value = None
        self.expected_temp_value = None

    def init_config(self):
        crt_folder_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(crt_folder_path, DCServiceConfigProvider.CONFIG_NAME)
        f = open(config_path)
        self.source_conf = json.load(f)

        return self

    def set_scheduled_message_send(self, state):
        LOGGER.info(f"Set new collectors/temp/enabled to: '{state}'")
        self.source_conf["collectors"]["temp"]["enabled"] = state

        LOGGER.info(f"Set new collectors/storage/enabled to: '{state}'")
        self.source_conf["collectors"]["storage"]["enabled"] = state

        LOGGER.info(f"Set new collectors/ram/enabled to: '{state}'")
        self.source_conf["collectors"]["ram"]["enabled"] = state

        return self

    def set_topic_prefix(self, prefix: str):
        prefix = prefix.replace('/', '')
        new_send_sd = f"/{prefix}{self.source_conf['collectors']['root_send']}" 
        LOGGER.info(f"Set new topic for sending data: '{new_send_sd}'")
        self.source_conf["collectors"]["root_send"] = new_send_sd

        new_send_qr = f"/{prefix}{self.source_conf['collectors']['root_query']}"
        LOGGER.info(f"Set new topic for quering data: '{new_send_qr}'")
        self.source_conf["collectors"]["root_query"] = new_send_qr

        return self

    def generate_dc_ram_file(self, value, path=None):
        LOGGER.info("Generating RAM file for tests")
        if path is None:
            if self.ram_path is None:
                _, path = tempfile.mkstemp(prefix='ram_')
            else:
                path = self.ram_path
        LOGGER.info(f"RAM file path: '{path}'")

        self.expected_ram_value = value

        content = "MemTotal:32644220 kB\nMemFree:985060 kB\nMemAvailable:23372996 kB"
        #  {"available":-1,"total":-1,"used":-1}  
        self.ram_path = write_to_file(path, content)

        return self

    def set_config_ram_path(self, path):
        LOGGER.info(f"Set new collectors/ram/extract_path to: '{path}'")
        self.source_conf["collectors"]["ram"]["extract_path"] = path

        return self

    def generate_dc_storage_file(self, value, path=None):
        LOGGER.info("Generating STORAGE file for tests")
        if path is None:
            if self.storage_path is None:
                _, path = tempfile.mkstemp(prefix='storage_')
            else:
                path = self.storage_path
        LOGGER.info(f"STORAGE file path: '{path}'")

        self.storage_path = path
        self.expected_storage_value = value

        return self

    def set_config_storage_path(self, path):
        LOGGER.info(f"Set new collectors/storage/extract_path to: '{path}'")
        self.source_conf["collectors"]["storage"]["extract_path"] = path

        return self

    def generate_dc_temp_file(self, value, path=None):
        LOGGER.info("Generating TEMP file for tests")
        if path is None:
            if self.temp_path is None:
                _, path = tempfile.mkstemp(prefix='temp_')
            else:
                path = self.temp_path
        LOGGER.info(f"TEMP file path: '{path}'")
        
        self.expected_temp_value = value
        
        content = self.expected_temp_value * 1000
        self.temp_path = write_to_file(path, content)

        return self

    def set_config_temp_path(self, path):
        LOGGER.info(f"Set new collectors/temp/extract_path to: '{path}'")
        self.source_conf["collectors"]["temp"]["extract_path"] = path

        return self

    def generate(self, path_prefix=None):
        if path_prefix is None:
            path_prefix = tempfile.gettempdir()
        LOGGER.info(f"Generating new config file in folder '{path_prefix}'")

        if not os.path.exists(path_prefix):
            os.makedirs(path_prefix)
        config_path = os.path.join(path_prefix, DCServiceConfigProvider.CONFIG_NAME)

        with open(config_path, "w") as fp:
            json.dump(self.source_conf, fp)

        self.config_path = os.path.dirname(os.path.abspath(config_path))

        return self
