import time

import docker
from src.applications.services.base_client import BaseClient
from src.config.config import CONFIG
from src.logger import SDVLogger
from src.helpers.helpers import write_to_file
import os

LOGGER = SDVLogger.get_logger("SDVDockerClient")


class BaseDockerClient(BaseClient):
    HAS_ARTIFACTS_TO_COLLECT = True
    container_name = None

    def __init__(self) -> None:
        self.client = docker.from_env()
        self.container = None

    def run(self):
        raise NotImplementedError("Run method needs to be implemented")

    def ensure_healthy(self, timeout=CONFIG.DOCKER_START_TIMEOUT):
        raise NotImplementedError("Run method needs to be implemented")

    def ensure_stop(self):
        for container in self.client.containers.list():
            LOGGER.info(container.name.lower())
            if container.name.lower() == self.container_name.lower():
                LOGGER.info(
                    f"Container '{container.id}:{container.name}' is running. Stoping it"
                )
                container.stop()

        return self

    def stop(self):
        LOGGER.info(f"Stoping '{self.container_name}' container")
        if self.check_running() is False:
            LOGGER.error(f"No active '{self.container_name}' container running")
            return self

        self.container.stop()

        return self

    def restart(self):
        if self.check_running() is False:
            LOGGER.warning(
                f"No active '{self.container_name}' container running. Starting new one"
            )
            return self.run()

        self.container.restart()

        return self

    def check_running(self):
        try:
            container = self.client.containers.get(self.container_name)
            container_state = container.attrs['State']
            return container_state['Status'] == 'running'
        except docker.errors.NotFound:
            return False

    def check_exists(self):
        try:
            container = self.client.containers.get(self.container_name)
            container_state = container.attrs['State']
            LOGGER.debug(f"'{self.container_name}' container exists. It's status is '{container_state}'")

            return True
        except docker.errors.NotFound:
            return False


    def expects_log_message(self, message, timeout=CONFIG.DOCKER_START_TIMEOUT):
        if self.check_exists() is False:
            LOGGER.error(f"No active '{self.container_name}' container running")
            return False

        timeout = time.time() + timeout
        while time.time() < timeout:
            actual_msg = str(message.lower())
            expected_msg = self.container.logs().decode("utf-8").lower()

            if actual_msg in expected_msg:
                LOGGER.info(f"Message '{message}' is found in {self.container_name}")
                return True
            time.sleep(1)

        LOGGER.warning(f"Message '{message}' is not found in {self.container_name}")
        return False

    def collect_artifacts(self, path_prefix):
        filename = f'docker_logs_{self.container_name}.log'
        path = os.path.join(path_prefix, filename)
        
        LOGGER.info(f"Collection docker container '{self.container_name}' artifacts into '{path}' folder")
        if self.check_exists() is True:
            context = self.container.logs(timestamps=True).decode("utf-8")
            return write_to_file(path, context)
        else:
            LOGGER.error(f"Collection docker container '{self.container_name}' artifacts is not possible. Container is not running")

    def remove(self):
        if self.check_exists() is True:
            container = self.client.containers.get(self.container_name)
            if self.check_running() is False:
                LOGGER.info(f"'{self.container_name}' is not runnning. Removing")
                container.remove()
            else:
                LOGGER.info(f"'{self.container_name}' is runnning. Stoping and Removing")
                container.stop()
                container.remove()
        LOGGER.info(f"'{self.container_name}' doesn't exist. Nothing to remove")
        return self