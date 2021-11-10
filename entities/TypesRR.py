from enum import Enum
from exceptions.NotResourceRecordTypeError import NotResourceRecordTypeError


class TypesRR(Enum):
    """
    This class represent all the types of resource records used in this application.

    """
    A = "A",
    CNAME = "CNAME",
    NS = "NS",
    MX = "MX"

    def to_string(self) -> str:
        """
        This method return a string representation of the type.

        Returns
        -------
        The string representation of the type.
        """
        return self.value[0]

    @staticmethod
    def parse_from_string(string: str) -> 'TypesRR':
        """
        This method return a string representation of the type.

        Parameters
        ----------
        string : `str`
            The string parameter.

        Returns
        -------
        The matched TypesRR enum.

        Raises
        ------
        NotResourceRecordTypeError
            If there is no match.
        """
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

    def __str__(self):
        return self.to_string()
