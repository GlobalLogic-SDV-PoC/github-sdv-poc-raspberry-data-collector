from src.enums.tc_management_adaptors import TCManagementAdaptors
from src.testcase_management.test_results_adaptors.adaptors.confluence_adaptor import ConfluenceAdaptor
from src.testcase_management.test_results_adaptors.adaptors.test_rail_adaptor import TestRailAdaptor
from src.testcase_management.test_results_adaptors.adaptors.xray_adaptor import XRayAdaptor


class AdaptorsProvider:
    MAPPER = {
        TCManagementAdaptors.CONFLUENCE: ConfluenceAdaptor,
        TCManagementAdaptors.TEST_RAIL: TestRailAdaptor,
        TCManagementAdaptors.X_RAY: XRayAdaptor,

    }

    @classmethod
    def get_providers(cls, modes):
        
        res = []
        for mode in modes:
            _mode = cls.MAPPER.get(mode)
            if _mode is None:
                raise NotImplementedError(f"Run Mode '{mode}' is not registered")

            res.append(_mode)
        
        return res