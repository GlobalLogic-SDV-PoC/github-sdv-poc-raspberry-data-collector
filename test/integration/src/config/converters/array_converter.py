from src.config.converters.base_converter import BaseConverter


class ArrayConverter(BaseConverter):
    CLASS = list

    @classmethod
    def convert(cls, val):
        if len(val) == 0:
            return []
        
        val = val.replace(" ", "")
        SEPARATORS = [',', ';', '|']

        arr = []
        for separator in SEPARATORS:
            if separator in val:
                arr = val.split(separator)
                return arr

        if len(arr) == 0:
            return [val]
