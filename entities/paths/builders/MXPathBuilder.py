from asyncio import InvalidStateError
from entities.paths.MXPath import MXPath
from entities.paths.Path import Path
from entities.RRecord import RRecord
from entities.paths.builders.PathBuilder import PathBuilder
from entities.enums.TypesRR import TypesRR
from exceptions.PathIntegrityError import PathIntegrityError


class MXPathBuilder(PathBuilder):
    def __init__(self):
        self.path = list()
        self.resolved = False

    def complete_resolution(self, rr: RRecord) -> 'MXPathBuilder':      # FORWARD DECLARATIONS (REFERENCES)
        if self.resolved:
            raise InvalidStateError
        if rr.type != TypesRR.MX:
            raise ValueError
        else:
            self.path.append(rr)
        if Path.check_path_integrity(self.path):
            self.resolved = True
            return self
        else:
            raise PathIntegrityError

    def add_alias(self, rr: RRecord) -> 'MXPathBuilder':        # FORWARD DECLARATIONS (REFERENCES)
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
            return MXPath(self.path)
        else:
            raise InvalidStateError
