from src.config.run_modes.modes.rules.base_rule import BaseRule
from src.enums.marks import Type
from src.logger import SDVLogger
from src.helpers.customize_marks import SDVMarks


LOGGER = SDVLogger.get_logger("TypePresent")


class TypePresent(BaseRule):

    @staticmethod
    def execute(test_item):
        LOGGER.info(f"Checking if test '{test_item.name}' has any of Type enum")
        marks = SDVMarks.get_list_of_marks(test_item)

        for mark in marks:
            if mark in Type.values_list():
                LOGGER.info(f"Mark '{mark}' is found amoung registered Type enum")
                return True
            
        LOGGER.warning("No marks from Type enum is found amoung registered")
        return False
