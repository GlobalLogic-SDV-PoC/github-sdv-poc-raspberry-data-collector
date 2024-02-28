class ClassNameRepr(type):
    def __repr__(cls):
        return cls.__name__


class BaseAdaptor(metaclass=ClassNameRepr):

    @classmethod
    def update_automation_status(cls, test_item):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")
    

    @classmethod
    def update_run_result(cls, test_item):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")