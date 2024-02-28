from src.config.run_modes.modes.rules.base_rule import BaseRule
from src.enums.marks import Priority
from src.logger import SDVLogger
from src.helpers.customize_marks import SDVMarks


LOGGER = SDVLogger.get_logger("PriorityPresent")


class PriorityPresent(BaseRule):

    @staticmethod
    def execute(test_item):
        LOGGER.info(f"Checking if test '{test_item.name}' has any of Priority enum")
        marks = SDVMarks.get_list_of_marks(test_item)

        for mark in marks:
            if mark in Priority.values_list():
                LOGGER.info(f"Mark '{mark}' is found amoung registered Priority enum")
                return True
            
        LOGGER.warning("No marks from Priority enum is found amoung registered")
        return False
