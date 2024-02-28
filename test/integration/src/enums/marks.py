from src.enums.extended_enum import ExtendedEnum


class FrameworkSpecific(ExtendedEnum):
    TO_BE_AUTOMATED = "to_be_automated"
    SKIP_IF_DEV = "skip_if_dev"


class Priority(ExtendedEnum):
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"
    P4 = "p4"


class Suite(ExtendedEnum):
    SMOKE = "smoke"
    REGRESSION = "regression"
    DATA_COLLECTOR = "data_collector"
    OTA_UPDATER = "ota_updater"


class Type(ExtendedEnum):
    SYSTEM = "system"
    INTEGRATION = "integration"


class Tasks(ExtendedEnum):
    TASK_123 = "task_123"
    TASK_124 = "task_124"
    TASK_125 = "task_125"
    TASK_126 = "task_126"
    TASK_127 = "task_127"
