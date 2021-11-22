from enum import Enum
from exceptions.NotROVStateTypeError import NotROVStateTypeError


class ROVStates(Enum):
    UNK = "UNK",
    INV = "INV",
    VLD = "VLD"

    def to_string(self) -> str:
        return str(self.value[0])

    @staticmethod
    def parse_from_string(string: str) -> 'ROVStates':
        if string == 'UNK' or string == 'unk' or string == 'UNKNOWN' or string == 'unknown':
            return ROVStates.UNK
        elif string == 'INV' or string == 'inv' or string == 'INVALID' or string == 'invalid':
            return ROVStates.INV
        elif string == 'VLD' or string == 'vld' or string == 'VALID' or string == 'valid':
            return ROVStates.VLD
        else:
            raise NotROVStateTypeError(string)

    def __str__(self):
        return self.to_string()
