import time

from src.config.config import CONFIG
from src.applications.cloud_cli.base_cloud_client import BaseCloudClient
from src.logger import SDVLogger
from azure.cli.core import get_default_cli

LOGGER = SDVLogger.get_logger("AZURE_CLIENT")


class AzureCliClient(BaseCloudClient):
    def __init__(self) -> None:
        super().__init__()
        self.thing = None
        self.cli_client = get_default_cli()

    @property
    def thing_name(self):
        return 'AZURE_THING_TO_TEST'

    @staticmethod
    def ecr_login():
        LOGGER.info("AZURE ECR Login")

    def init_cli(self):
        LOGGER.info("Initializing AZURE CLI ")
        return self
        
        self \
            ._login() \
            ._add_extension() \
                
        
        return self

    # def _create_group(self):
    #     LOGGER.info("Invoke az iot hub device-identity create -d {DeviceName} -n {YourIoTHubName}")
    #     self._invoke_cmd(
    #         ['group', 'create', '--name', self.GROUP_NAME, '--location', CONFIG.AZURE_REGION]
    #         )

    #     return self
    
    def _add_extension(self):
        LOGGER.info("Invoke extension add --name azure-iot")
        self._invoke_cmd(
            ['extension' 'add', '--name', 'azure-iot']
            )

        return self

    def _login(self):
        LOGGER.info("Invoke AZURE CLI Login")
        self._invoke_cmd(
            ['login', '--service-principal', '-u', '111', '-p', '123','--tenant', '1234']
            )

        return self


    def tear_up_thing(self, name):
        LOGGER.info("IOT Thing tear up")
        LOGGER.info(f"IOT Thing tear up: {self.cli_client.get_cli_version()}")

        return self

    def tear_down_thing(self):
        LOGGER.info("IOT Thing tear down")

        return self

    def connect_to_message_bus(self):
        LOGGER.info(f"Connecting to AZURE IOT MQTT endpoint'")

        return self

    def subscribe_to_topic(self, message_topic):
        LOGGER.info(f"Subscribing to topic '{message_topic}'...")

        return self

    def publish_message(self, message_topic, message):
        LOGGER.info(f"Publishing message to topic '{message_topic}': {message}")

    def expects_message(self, topic, message, timeout=10):
        timeout = time.time() + timeout
        while time.time() < timeout:
            m = self.read_message(topic)
            if m == message:
                LOGGER.info(f"Message {m} retrieved")
                return m

        raise TimeoutError(f"Timeout limit reached. No {m} message retrived")

    def terminate(self):
        LOGGER.info("Disconecting from AZURE IOT")

        return self

    def _invoke_cmd(self, args_str):
        # args = args_str.split()
        self.cli_client.invoke(args_str)
        if self.cli_client.result.result:
            return self.cli_client.result.result
        elif self.cli_client.result.error:
            raise self.cli_client.result.error
        return True