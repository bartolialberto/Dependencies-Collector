from typing import List
from entities.paths.Path import Path
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.PathIntegrityError import PathIntegrityError


class MXPath(Path):
    """
    This class implements the Path class with a type MX resource record as resolution.

    ...

    Attributes
    ----------
    __path : List[RRecord]
        List of resource records, accessible through the path property as defined in the Path abstract class.
    """
    def __init__(self, rr_list: List[RRecord]):
        """
        Initialize the object.

        :param rr_list: List of resource records.
        :type rr_list: List[RRecord]
        :raise PathIntegrityError: If the list of resource records is not compliant as path.
        :raise ValueError: If resource records are not of the expected type.
        """
        if not Path.check_path_integrity(rr_list):
            raise PathIntegrityError
        if rr_list[-1].type != TypesRR.MX:
            raise ValueError("Path doesn't resolve in a MX type RR.")
        for rr in rr_list[0:-1]:
            if rr.type != TypesRR.CNAME:
                raise ValueError
        self.__path = rr_list

    @property
    def path(self) -> List[RRecord]:
        return self.__path
