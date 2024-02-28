from src.config.run_modes.modes.rules.base_rule import BaseRule
from src.enums.marks import Tasks
from src.logger import SDVLogger
from src.helpers.customize_marks import SDVMarks


LOGGER = SDVLogger.get_logger("TaskPresent")


class TaskPresent(BaseRule):

    @staticmethod
    def execute(test_item):
        LOGGER.info(f"Checking if test '{test_item.name}' has any of TASKS enum")
        marks = SDVMarks.get_list_of_marks(test_item)

        for mark in marks:
            if mark in Tasks.values_list():
                LOGGER.info(f"Mark '{mark}' is found amoung registered TASKS enum")
                return True
            
        LOGGER.warning("No marks from TASKS enum is found amoung registered")
        return False
