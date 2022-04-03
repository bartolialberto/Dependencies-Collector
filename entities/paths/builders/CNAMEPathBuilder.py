from asyncio import InvalidStateError
from entities.paths.CNAMEPath import CNAMEPath
from entities.paths.Path import Path
from entities.RRecord import RRecord
from entities.paths.builders.PathBuilder import PathBuilder
from entities.enums.TypesRR import TypesRR
from exceptions.PathIntegrityError import PathIntegrityError
from exceptions.UselessMethodInvocationError import UselessMethodInvocationError


class CNAMEPathBuilder(PathBuilder):
    def __init__(self):
        self.path = list()
        self.resolved = False

    def complete(self) -> 'CNAMEPathBuilder':       # FORWARD DECLARATIONS (REFERENCES)
        if self.resolved:
            raise InvalidStateError
        try:
            resolution_rr = self.path.pop()
        except IndexError:
            raise
        return self.complete_resolution(resolution_rr)

    def complete_resolution(self, rr: RRecord) -> 'CNAMEPathBuilder':       # FORWARD DECLARATIONS (REFERENCES)
        if self.resolved:
            raise InvalidStateError
        if rr.type != TypesRR.CNAME:
            raise ValueError
        else:
            self.path.append(rr)
        if Path.check_path_integrity(self.path):
            self.resolved = True
            return self
        else:
            raise PathIntegrityError

    def add_alias(self, rr: RRecord) -> 'CNAMEPathBuilder':     # FORWARD DECLARATIONS (REFERENCES)
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
            return CNAMEPath(self.path)
        else:
            raise InvalidStateError
