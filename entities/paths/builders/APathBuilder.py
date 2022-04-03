from asyncio import InvalidStateError
from entities.paths.APath import APath
from entities.paths.CNAMEChain import CNAMEPath
from entities.paths.Path import Path
from entities.paths.builders.PathBuilder import PathBuilder
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.PathIntegrityError import PathIntegrityError


class APathBuilder(PathBuilder):
    def __init__(self):
        self.path = list()
        self.resolved = False

    def complete_resolution(self, rr: RRecord) -> 'APathBuilder':       # FORWARD DECLARATIONS (REFERENCES)
        if self.resolved:
            raise InvalidStateError
        if rr.type != TypesRR.A:
            raise ValueError
        else:
            self.path.append(rr)
        if Path.check_path_integrity(self.path):
            self.resolved = True
            return self
        else:
            raise PathIntegrityError

    def add_alias(self, rr: RRecord) -> 'APathBuilder':     # FORWARD DECLARATIONS (REFERENCES)
        if self.resolved:
            raise InvalidStateError
        if rr.type != TypesRR.CNAME:
            raise ValueError
        else:
            self.path.append(rr)
        if Path.check_path_integrity(self.path):
            return self
        else:
            raise PathIntegrityError

    def build(self) -> Path:
        if self.resolved:
            return APath(self.path)
        else:
            raise InvalidStateError

    @staticmethod
    def from_cname_path(cname_path: CNAMEPath) -> 'APathBuilder':       # FORWARD DECLARATIONS (REFERENCES)
        a_pb = APathBuilder()
        for rr in cname_path.get_list():
            a_pb.add_alias(rr)
        return a_pb
