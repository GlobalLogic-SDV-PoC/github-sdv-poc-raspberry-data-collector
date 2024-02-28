from src.config.validators.base_validator import BaseValidator
from src.logger import SDVLogger

LOGGER = SDVLogger.get_logger("OPTIONAL_VALIDATOR")


class OptonalValidator(BaseValidator):
    
    @staticmethod
    def validate(name, value):
        # since no check for optional value - no condition is needed
        LOGGER.info(f"Variable '{name}' is valid with '{value}' value.")
