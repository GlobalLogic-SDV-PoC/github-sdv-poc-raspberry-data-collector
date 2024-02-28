from src.testcase_management.test_results_adaptors.adaptors.base_adaptor import BaseAdaptor
from src.logger import SDVLogger

LOGGER = SDVLogger.get_logger("XRayAdaptor")


class XRayAdaptor(BaseAdaptor):

    @classmethod
    def update_automation_status(cls, test_item):
        LOGGER.info(f"Updating status of automation for {test_item.name} test")
        

    @classmethod
    def update_run_result(cls, test_item):
        LOGGER.info(f"Updating test result of automation for {test_item.name} test")
