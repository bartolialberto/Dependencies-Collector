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
        if string == TypesRR.A.value:
            return TypesRR.A
        elif string == TypesRR.CNAME.value:
            return TypesRR.CNAME
        elif string == TypesRR.NS.value:
            return TypesRR.NS
        elif string == TypesRR.MX.value:
            return TypesRR.MX
        else:
            raise NotResourceRecordTypeError(string)

