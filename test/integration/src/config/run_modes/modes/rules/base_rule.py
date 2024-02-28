class ClassNameRepr(type):
    def __repr__(cls):
        return cls.__name__


class BaseRule(metaclass=ClassNameRepr):

    @staticmethod
    def execute(test_item):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")