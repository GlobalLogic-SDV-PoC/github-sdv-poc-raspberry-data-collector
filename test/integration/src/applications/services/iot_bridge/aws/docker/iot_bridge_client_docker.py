from src.applications.services.base_docker_client import BaseDockerClient
from src.applications.services.iot_bridge.aws.docker.config_provider.config_iot_bridge_service_provider import \
    IotBridgeServiceConfigProvider
from src.config.config import CONFIG
from src.logger import SDVLogger

LOGGER = SDVLogger.get_logger("IotBridgeClientDocker")


class IotBridgeClientDocker(BaseDockerClient):
    container_name = "raspberry-aws-iot-bridge"
    tag = CONFIG.IOTBRIDGE_DOCKER_TAG

    VOLUMES = {
        "CONFIG": "/var/configs",
        "CERTS": "/var/security/",
    }

    def __init__(self, thing_name, certs_folder) -> None:
        super().__init__()
        self.thing_name = thing_name
        self.config = IotBridgeServiceConfigProvider(certs_folder=certs_folder)
        self.volumes = None

    def tear_up(self):
        LOGGER.info(f"Tearing up '{self.container_name}' service.")

        self.init_service_config(self.thing_name).ensure_stop().remove().pull().map_volume(
            [
                f"{self.config.config_path}:{self.VOLUMES['CONFIG']}",
                f"{self.config.certs_folder}:{self.VOLUMES['CERTS']}",
            ]
        ).run().ensure_healthy()

        return self

    def tear_down(self):
        LOGGER.info(f"Tearing down '{self.container_name}' service.")
        self.stop()

        return self

    def init_service_config(self, thing_name):
        LOGGER.info(f"Initializing the config for '{thing_name}' thing")

        self.config.init_config().set_client_id(thing_name).generate(
            CONFIG.IOTBRIDGE_CONFIG_FOLDER
        )

        return self

    def map_volume(self, volumes):
        LOGGER.info(f"Mapping volumes: {volumes}")

        self.volumes = volumes

        return self

    def pull(self):
        LOGGER.info(f"Updating {self.container_name} image with tag '{self.tag}'"),

        repository = f"{CONFIG.Account_ID}.dkr.ecr.{CONFIG.AWS_REGION}.amazonaws.com/{self.container_name}"
        self.client.images.pull(repository, self.tag)

        return self

    def run(self):
        LOGGER.info(f"Starting {self.container_name} container")
        self.container = self.client.containers.run(
            f"{CONFIG.Account_ID}.dkr.ecr.{CONFIG.AWS_REGION}.amazonaws.com/{self.container_name}:{self.tag}",
            detach=True,
            auto_remove=False,
            name=self.container_name,
            tty=True,
            init=True,
            ports={"5555": "5555"},
            volumes=self.volumes,
        )

        return self

    def ensure_healthy(self, timeout=CONFIG.DOCKER_START_TIMEOUT):
        LOGGER.info(f"Ensure container '{self.container_name}' healthy")

        msg = f"connected, client id: {self.thing_name}"
        res = self.expects_log_message(msg, timeout)
        if res is True:
            LOGGER.info(f"container {self.container_name} is healthy. '{msg}' is found")
        else:
            LOGGER.warning(
                f"container {self.container_name} is unhealthy. '{msg}' is not found"
            )

        # msg = 'Exception ocurred trying to set connection promise (likely already set)'
        # res = self.expects_log_message(msg, 30)
        # if res is False:
        #     LOGGER.info(f"container {self.container_name} is healthy. '{msg}' is not found")
        # else:
        #     LOGGER.warning(f"container {self.container_name} is unhealthy. '{msg}' is found")

        return self
