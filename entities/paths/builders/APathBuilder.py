from asyncio import InvalidStateError
from typing import List
from entities.paths.APath import APath
from entities.paths.CNAMEPath import CNAMEPath
from entities.paths.Path import Path
from entities.paths.builders.PathBuilder import PathBuilder
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.PathIntegrityError import PathIntegrityError


class APathBuilder(PathBuilder):
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

    def complete_resolution(self, rr: RRecord) -> 'APathBuilder':       # FORWARD DECLARATIONS (REFERENCES)
        if self.is_resolved:
            raise InvalidStateError
        if rr.type != TypesRR.A:
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
            return APath(self.constructing_path)
        else:
            raise InvalidStateError

    @staticmethod
    def from_cname_path(cname_path: CNAMEPath) -> 'APathBuilder':       # FORWARD DECLARATIONS (REFERENCES)
        a_pb = APathBuilder()
        for rr in cname_path.path:
            a_pb.add_alias(rr)
        return a_pb
