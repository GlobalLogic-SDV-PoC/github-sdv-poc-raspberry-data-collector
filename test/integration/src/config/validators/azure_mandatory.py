import os

from src.config.validators.base_validator import BaseValidator
from src.enums.cloud_providers import CloudProviders
from src.logger import SDVLogger

LOGGER = SDVLogger.get_logger("AZURE_MANDATORY_VALIDATOR")


class AzureMandatoryValidator(BaseValidator):
    
    @staticmethod
    def validate(name, value):
        cloud_provider = os.environ.get("CLOUD_PROVIDER")

        if cloud_provider == CloudProviders.AZURE:
            if value is not None:
                LOGGER.info(
                    f"Variable '{name}' is valid with '{value}' value for '{cloud_provider}' cloud provider'."
                )
            else:
                raise ValueError(
                    f"Variable '{name}' is mandatory, but it has '{value}' value for '{cloud_provider}' cloud provider"
                )