from enum import Enum
from exceptions.NotROVStateTypeError import NotROVStateTypeError


class ROVStates(Enum):
    """
    This class represents all the states of a ROV in the ROVPage (web page).

    """
    UNK = "UNK",
    INV = "INV",
    VLD = "VLD",

    def to_string(self) -> str:
        """
        This method returns a string representation of the type, which is also the exact representation used in the web
        page.

        :returns: The string representation of the type.
        :rtype: str
        """
        return str(self.value[0])

    @staticmethod
    def parse_from_string(string: str) -> 'ROVStates':
        """
        This method parses a string and returns if it match a representation of one of the types.

        :param string: The string parameter.
        :type string: str
        :raise NotROVStateTypeError: If there is no match.
        :returns: The matched ROVStates enum.
        :rtype: ROVStates
        """
        if string == 'UNK' or string == 'unk' or string == 'UNKNOWN' or string == 'unknown':
            return ROVStates.UNK
        elif string == 'INV' or string == 'inv' or string == 'INVALID' or string == 'invalid':
            return ROVStates.INV
        elif string == 'VLD' or string == 'vld' or string == 'VALID' or string == 'valid':
            return ROVStates.VLD
        else:
            raise NotROVStateTypeError(string)

    def __str__(self):
        """
        This method returns a string representation of this object.

        :return: A string representation of this object.
        :rtype: str
        """
        return self.to_string()
