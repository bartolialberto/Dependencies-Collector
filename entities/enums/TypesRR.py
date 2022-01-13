from enum import Enum
from exceptions.NotResourceRecordTypeError import NotResourceRecordTypeError


class TypesRR(Enum):
    """
    This class represents all the types of resource records used in this application.

    """
    A = "A",
    CNAME = "CNAME",
    NS = "NS",
    MX = "MX",

    def to_string(self) -> str:
        """
        This method returns a string representation of the type.

        :returns: The string representation of the type.
        :rtype: str
        """
        return self.value[0]

    @staticmethod
    def parse_from_string(string: str) -> 'TypesRR':
        """
        This method parses a string and returns if it match a representation of one of the types.

        :param string: The string parameter.
        :type string: str
        :raise NotResourceRecordTypeError: If there is no match.
        :returns: The matched TypesRR enum.
        :rtype: TypesRR
        """
        if string == 'A' or string == 'a':
            return TypesRR.A
        elif string == 'CNAME' or string == 'cname' or string == 'Cname':
            return TypesRR.CNAME
        elif string == 'NS' or string == 'ns' or string == 'Ns':
            return TypesRR.NS
        elif string == 'MX' or string == 'mx' or string == 'Mx':
            return TypesRR.MX
        else:
            raise NotResourceRecordTypeError(string)

    def __str__(self):
        """
        This method returns a string representation of this object.

        :return: A string representation of this object.
        :rtype: str
        """
        return self.to_string()
