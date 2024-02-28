from src.config.run_modes.modes.base_run_mode import BaseRunMode
from src.logger import SDVLogger
from src.config.run_modes.modes.rules.priority_present import PriorityPresent
from src.config.run_modes.modes.rules.suite_present import SuitePresent
from src.config.run_modes.modes.rules.task_present import TaskPresent
from src.config.run_modes.modes.rules.type_present import TypePresent


LOGGER = SDVLogger.get_logger("DebugRunMode")


class DebugRunMode(BaseRunMode):
    TEST_WHITE_LIST = [
    ]
    MANDATORY_VALIDATORS = [
    ]
    WARN_VALIDATORS = [
        PriorityPresent,
        SuitePresent,
        TaskPresent,
        TypePresent
    ]
