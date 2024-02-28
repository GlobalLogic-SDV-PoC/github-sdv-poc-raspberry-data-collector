from src.applications.services.base_docker_client import BaseDockerClient
from src.applications.services.data_collector.aws.docker.config_provider.config_dc_service_provider import \
    DCServiceConfigProvider
from src.config.config import CONFIG
from src.logger import SDVLogger
from uuid import uuid4


LOGGER = SDVLogger.get_logger("DataCollectorClient")


class DataCollectorDockerClient(BaseDockerClient):
    container_name = "raspberry-data-collector"
    tag = CONFIG.DATACOLLECTOR_DOCKER_TAG

    VOLUMES = {
        "RAM_PATH": "/var/testdata/ram",
        "TEMP_PATH": "/var/testdata/temp",
        "STORAGE_PATH": "/var/testdata/storage",
        "CONFIG_PATH": "/var/configs",
    }

    def __init__(self) -> None:
        super().__init__()
        self.config = DCServiceConfigProvider()
        self.volumes = None

    def tear_up(self):
        LOGGER.info(f"Tearing up '{self.container_name}' service.")
        self.init_config().ensure_stop().remove().pull().map_volume(
            [
                f"{self.config.config_path}:{self.VOLUMES['CONFIG_PATH']}",
                f"{self.config.ram_path}:{self.VOLUMES['RAM_PATH']}",
                f"{self.config.temp_path}:{self.VOLUMES['TEMP_PATH']}",
                # f"{self.config.storage_path}:{self.VOLUMES['STORAGE_PATH']}",
            ]
        ).run().ensure_healthy().ensure_connected()

        return self

    def tear_down(self):
        LOGGER.info(f"Tearing down '{self.container_name}' service.")
        self.stop()

        return self

    def init_config(self):
        LOGGER.info(f"Initializing config for '{self.container_name}' container"),

        self.config \
            .init_config() \
            .set_scheduled_message_send(False) \
            .set_topic_prefix(str(uuid4())) \
            .generate_dc_ram_file(10) \
            .set_config_ram_path(self.VOLUMES["RAM_PATH"]) \
            .generate_dc_temp_file(99) \
            .set_config_temp_path(DataCollectorDockerClient.VOLUMES["TEMP_PATH"]) \
            .generate()
            # .generate_dc_storage_file(CONFIG.DC_STORAGE_FILE, 100) \
            # .set_config_storage_path(self.VOLUMES["STORAGE_PATH"]) \

        return self

    def pull(self):
        LOGGER.info(
            f"Updating {self.container_name} image with tag '{DataCollectorDockerClient.tag}'"
        ),

        repository = f"{CONFIG.Account_ID}.dkr.ecr.{CONFIG.AWS_REGION}.amazonaws.com/{self.container_name}"
        self.client.images.pull(repository, DataCollectorDockerClient.tag)

        return self

    def map_volume(self, volumes):
        LOGGER.info(f"Mapping volumes: {volumes} to container '{self.container_name}'")
        self.volumes = volumes

        return self

    def run(self):
        LOGGER.info(f"Starting '{self.container_name}' container")
        self.container = self.client.containers.run(
            f"{CONFIG.Account_ID}.dkr.ecr.{CONFIG.AWS_REGION}.amazonaws.com/{self.container_name}:{self.tag}",
            detach=True,
            network_mode="host",
            auto_remove=False,
            name=self.container_name,
            volumes=self.volumes,
        )

        return self

    def ensure_healthy(self, timeout=CONFIG.DOCKER_START_TIMEOUT):
        msg = "connected: 127.0.0.1:5555"
        res = self.expects_log_message(msg, timeout)
        if res is True:
            LOGGER.info(f"container {self.container_name} is healthy")
        else:
            LOGGER.warning(f"container {self.container_name} is unhealthy")

        return self

    def ensure_connected(self, timeout=CONFIG.DOCKER_LOG_TIMEOUT):
        topic = self.config.source_conf["collectors"]["root_query"]
        msgs = [
            f'"action":"subscribe","topic":"{topic}/storage"',
            f'"action":"subscribe","topic":"{topic}/temp"',
            f'"action":"subscribe","topic":"{topic}/ram"',
        ]
        res = True
        for msg in msgs:
            res = self.expects_log_message(msg, timeout)

        if res is True:
            LOGGER.info(f"container {self.container_name} is connected to aws-client")
        else:
            LOGGER.warning(
                f"container {self.container_name} is not connected to aws-client"
            )

        return self


# aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 203647640528.dkr.ecr.eu-west-1.amazonaws.com
# docker pull 203647640528.dkr.ecr.eu-west-1.amazonaws.com/raspberry-aws-iot-bridge:latest
# docker run --network=host -d --rm -p 5555:5555 203647640528.dkr.ecr.eu-west-1.amazonaws.com/raspberry-aws-iot-bridge:latest -t --init