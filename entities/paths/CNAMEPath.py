from typing import List
from entities.paths.Path import Path
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.PathIntegrityError import PathIntegrityError


class CNAMEPath(Path):
    """
    This class implements the Path class with a type CNAME resource record as resolution.

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
        for rr in rr_list:
            if rr.type != TypesRR.CNAME:
                raise ValueError
        self.__path = rr_list

    @property
    def path(self) -> List[RRecord]:
        return self.__path
