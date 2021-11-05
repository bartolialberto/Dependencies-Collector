from enum import Enum
from exceptions.NotResourceRecordTypeError import NotResourceRecordTypeError


class TypesRR(Enum):
    A = "A",
    CNAME = "CNAME",
    NS = "NS",
    MX = "MX"

    def to_string(self):
        return self.value[0]

    @staticmethod
    def parse_from_string(string: str):
        if string == TypesRR.A.value[0]:
            return TypesRR.A
        elif string == TypesRR.CNAME.value[0]:
            return TypesRR.CNAME
        elif string == TypesRR.NS.value[0]:
            return TypesRR.NS
        elif string == TypesRR.MX.value[0]:
            return TypesRR.MX
        else:
            raise NotResourceRecordTypeError(string)

