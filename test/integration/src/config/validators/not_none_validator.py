from src.config.validators.base_validator import BaseValidator
from src.logger import SDVLogger

LOGGER = SDVLogger.get_logger("NOT_NONE_VALIDATOR")


class NotNoneValidator(BaseValidator):
    
    @staticmethod
    def validate(name, value):
        if value is not None:
            LOGGER.info(f"Variable '{name}' is valid with '{value}' value.")
        else:
            raise ValueError(
                f"Variable '{name}' is mandatory, but it has '{value}' value."
            )
