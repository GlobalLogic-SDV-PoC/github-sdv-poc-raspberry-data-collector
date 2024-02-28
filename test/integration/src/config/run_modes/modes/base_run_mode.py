from src.logger import SDVLogger

LOGGER = SDVLogger.get_logger("BaseRunMode")

class ClassNameRepr(type):
    def __repr__(cls):
        return cls.__name__


class BaseRunMode(metaclass=ClassNameRepr):
    TEST_WHITE_LIST = []
    MANDATORY_VALIDATORS = []
    WARN_VALIDATORS = []

    @classmethod
    def validate_test(cls, test_item):
        cls._warn_validate_test(test_item=test_item)
        
        return cls._mandatory_validate_test(test_item=test_item)

    @classmethod
    def _warn_validate_test(cls, test_item):
        if len(cls.WARN_VALIDATORS) == 0:
            return True
        
        LOGGER.info(f"Validate '{test_item.name}' test. Optional validation rules: '{cls.WARN_VALIDATORS}'")
        if test_item.name in cls.TEST_WHITE_LIST:
            LOGGER.info(f"Skip '{test_item.name}' test validation since it is in WHITE LIST")

        for validator in cls.WARN_VALIDATORS:
            validator.execute(test_item=test_item)
        
        return True
    
    @classmethod
    def _mandatory_validate_test(cls, test_item):
        if len(cls.MANDATORY_VALIDATORS) == 0:
            return True
        
        LOGGER.info(f"Validate '{test_item.name}' test. Mandatory validation rules: '{cls.MANDATORY_VALIDATORS}'")
        if test_item.name in cls.TEST_WHITE_LIST:
            LOGGER.info(f"Skip '{test_item.name}' test validation since it is in WHITE LIST")

        for validator in cls.MANDATORY_VALIDATORS:
            res = validator.execute(test_item=test_item)
            if res is False:
                LOGGER.error(f"Cannot proceed with running tests, since '{validator}' rule dissalowing run")
                return res

        return True