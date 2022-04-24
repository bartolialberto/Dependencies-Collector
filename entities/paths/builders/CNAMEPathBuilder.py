from asyncio import InvalidStateError
from typing import List
from entities.paths.CNAMEPath import CNAMEPath
from entities.paths.Path import Path
from entities.RRecord import RRecord
from entities.paths.builders.PathBuilder import PathBuilder
from entities.enums.TypesRR import TypesRR
from exceptions.PathIntegrityError import PathIntegrityError


class CNAMEPathBuilder(PathBuilder):
    def __init__(self):
        self.__path = list()
        self.__resolved = False

    @property
    def constructing_path(self) -> List[RRecord]:
        return self.__path

    @property
    def is_resolved(self) -> bool:
        return self.__resolved

    @is_resolved.setter
    def is_resolved(self, new_val: bool) -> None:
        self.__resolved = new_val

    def complete(self) -> 'CNAMEPathBuilder':       # FORWARD DECLARATIONS (REFERENCES)
        if self.is_resolved:
            raise InvalidStateError
        try:
            resolution_rr = self.constructing_path.pop()
        except IndexError:
            raise
        return self.complete_resolution(resolution_rr)

    def complete_resolution(self, rr: RRecord) -> 'CNAMEPathBuilder':       # FORWARD DECLARATIONS (REFERENCES)
        if self.is_resolved:
            raise InvalidStateError
        if rr.type != TypesRR.CNAME:
            raise ValueError
        else:
            self.constructing_path.append(rr)
        if Path.check_path_integrity(self.constructing_path):
            self.is_resolved = True
            return self
        else:
            raise PathIntegrityError

    def build(self) -> Path:
        if self.is_resolved:
            return CNAMEPath(self.constructing_path)
        else:
            raise InvalidStateError
