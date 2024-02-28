import json
import os

from src.logger import SDVLogger

LOGGER = SDVLogger.get_logger("CONFIG_IOTBRIDGE")


class IotBridgeServiceConfigProvider:
    CONFIG_NAME = "main_config.json"

    def __init__(self, certs_folder) -> None:
        self.source_conf = None
        self.config_path = None
        self.certs_folder = certs_folder

    def init_config(self):
        crt_folder_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(crt_folder_path, self.CONFIG_NAME)
        f = open(config_path)
        self.source_conf = json.load(f)

        return self

    def set_client_id(self, new_client_id):
        LOGGER.info(f"Set new client id: '{new_client_id}'")
        self.source_conf["iot"]["clientId"] = new_client_id

        return self

    def generate(self, path_prefix):
        LOGGER.info(f"Generating new config file in folder '{path_prefix}'")

        if not os.path.exists(path_prefix):
            os.makedirs(path_prefix)
        config_path = os.path.join(path_prefix, self.CONFIG_NAME)

        with open(config_path, "w") as fp:
            json.dump(self.source_conf, fp)

        self.config_path = os.path.dirname(os.path.abspath(config_path))

        return self
