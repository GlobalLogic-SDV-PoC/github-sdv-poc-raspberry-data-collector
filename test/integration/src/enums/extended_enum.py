from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def values_list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list(cls):
        return list(cls)
