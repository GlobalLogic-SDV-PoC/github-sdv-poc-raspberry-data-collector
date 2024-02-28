import os
import sys

from src.config.converters.base_converter import BaseConverter
from src.config.converters.int_converter import IntConverter
from src.config.converters.string_converter import StringConverter
from src.config.converters.array_converter import ArrayConverter
from src.config.converters.bool_converter import BoolConverter
from src.config.providers.config_from_defults_provider import \
    ConfigFromDefaultsProvider
from src.config.providers.config_from_env_provider import ConfigFromEnvProvider
from src.config.validators.aws_mandatory import AwsMandatoryValidator
from src.config.validators.base_validator import BaseValidator
from src.config.validators.optional_validator import OptonalValidator
from src.config.validators.not_none_validator import NotNoneValidator
from src.enums.cloud_providers import CloudProviders
from src.enums.platforms import Platforms
from src.enums.run_modes import RunModes
from src.enums.docker_tags import DockerTags
from src.enums.tc_management_adaptors import TCManagementAdaptors


class Config:
    DEFAULT_PLATFORM = Platforms.RASPBERRY

    def __init__(self) -> None:
        self.conf_dict = {}

        platform = os.environ.get("PLATFORM")
        if platform is None:
            platform = Config.DEFAULT_PLATFORM

        # json_path = f"src/config/env_configs/{platform}.json" #enable once needed
        env_file = os.path.join(
                        "src",
                        ".env"
                    )

        # Hierarhy of providers
        self.providers = [
            ConfigFromEnvProvider(env_file),
            # ConfigFromSimpleJsonProvider(json_path), #enable once needed
            ConfigFromDefaultsProvider(
                {
                    "TIMEOUT_COMMON": 30,
                    "PYTHON_VERSION": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    "DOCKER_START_TIMEOUT": 60,
                    "DOCKER_LOG_TIMEOUT": 10,
                    "IOTBRIDGE_AWS_CERTS_FOLDER": os.path.join(
                        "src",
                        "applications",
                        "services",
                        "iot_bridge",
                        "aws",
                        "docker",
                        "docker_volumes",
                        "certs",
                    ),
                    "IOTBRIDGE_CONFIG_FOLDER": os.path.join(
                        "src",
                        "applications",
                        "services",
                        "iot_bridge",
                        "aws",
                        "docker",
                        "docker_volumes",
                        "configs",
                    ),
                    # FOR LOCAL DEBUG ONLY NEVER COMMIT
                    # Use .env file in the root of test framework instead

                    "PLATFORM": Platforms.RASPBERRY,
                    "CLOUD_PROVIDER": CloudProviders.AWS,
                    "RUN_MODE": RunModes.STRICT,
                    "TC_ADAPTERS": f"{TCManagementAdaptors.CONFLUENCE}, {TCManagementAdaptors.TEST_RAIL}",
                    "DATACOLLECTOR_DOCKER_TAG": "b020013d6df28ae148d707947b68006059d1a7bc",
                    "IOTBRIDGE_DOCKER_TAG": DockerTags.LATEST,
                    "OTAUPDATER_DOCKER_TAG": DockerTags.LATEST,
                    "Account_ID": "203647640528",
                    "AWS_REGION": "eu-west-1",
                    "ARTIFACTS_COLLECT": "true",
                    "ARTIFACTS_FOLDER": os.path.join("reports","artifacts"),
                }
            ),
        ]

        # COMMON VAR SECTION
        self.register("TIMEOUT_COMMON", IntConverter, NotNoneValidator)
        self.register("PYTHON_VERSION", StringConverter, NotNoneValidator)
        self.register("DOCKER_START_TIMEOUT", IntConverter, NotNoneValidator)
        self.register("DOCKER_LOG_TIMEOUT", IntConverter, NotNoneValidator)
        self.register("PLATFORM", StringConverter, NotNoneValidator)
        self.register("CLOUD_PROVIDER", StringConverter, NotNoneValidator)
        self.register("RUN_MODE", StringConverter, NotNoneValidator)
        self.register("TC_ADAPTERS", ArrayConverter, OptonalValidator)

        # CICD SECTION
        self.register("DATACOLLECTOR_DOCKER_TAG", StringConverter, NotNoneValidator)
        self.register("IOTBRIDGE_DOCKER_TAG", StringConverter, NotNoneValidator)
        self.register("OTAUPDATER_DOCKER_TAG", StringConverter, NotNoneValidator)
        self.register("ARTIFACTS_COLLECT", BoolConverter, OptonalValidator)
        self.register("ARTIFACTS_FOLDER", StringConverter, OptonalValidator)

        # AWS CLOUD SECTION
        self.register("AWS_REGION", StringConverter, AwsMandatoryValidator)
        self.register("Account_ID", StringConverter, AwsMandatoryValidator)

        # AZURE CLOUD SECTION

        # IOT BRIDGE SERVICE SECTION
        self.register("IOTBRIDGE_AWS_CERTS_FOLDER", StringConverter, NotNoneValidator)
        self.register("IOTBRIDGE_CONFIG_FOLDER", StringConverter, NotNoneValidator)

        # DATA COLLECTOR SERVICE SECTION

        # UPDATER SERVICE SECTION

    def register(self, name: str, converter: BaseConverter, validator: BaseValidator):
        """
        Register name of the key which is used
        in tests
        """

        # Order in self.provider makes difference
        for provider in self.providers:
            val = provider.get(name)

            if val is not None:
                self.conf_dict[name] = converter.convert(val)
                break

        # raise error if no value is found across the providers
        val = self.conf_dict.get(name)
        if val is None:
            raise Exception(
                f"{name} variable cannot be found among values in registered config providers"
            )

        validator.validate(name, val)

    def __getattr__(self, name):
        """
        Return existing value
        """

        val = self.conf_dict.get(name)
        if val is None:
            raise Exception(f"{name} variable is not registered in config")

        return self.conf_dict.get(name)


# python way singleton
CONFIG = Config()
