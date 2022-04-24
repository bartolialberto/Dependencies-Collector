import abc
from asyncio import InvalidStateError
from typing import List
from entities.enums.TypesRR import TypesRR
from entities.paths.Path import Path
from entities.RRecord import RRecord
from exceptions.PathIntegrityError import PathIntegrityError


class PathBuilder(abc.ABC):
    @property
    @abc.abstractmethod
    def constructing_path(self) -> List[RRecord]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_resolved(self) -> bool:
        raise NotImplementedError

    @is_resolved.setter
    @abc.abstractmethod
    def is_resolved(self, new_val: bool) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def complete_resolution(self, rr: RRecord) -> 'PathBuilder':        # FORWARD DECLARATIONS (REFERENCES)
        # TODO: get type from rr
        raise NotImplementedError

    def add_alias(self, rr: RRecord) -> 'PathBuilder':      # FORWARD DECLARATIONS (REFERENCES)
        if self.is_resolved:
            raise InvalidStateError
        if rr.type != TypesRR.CNAME:
            raise ValueError
        else:
            self.constructing_path.append(rr)
        if Path.check_path_integrity(self.constructing_path):
            return self
        else:
            raise PathIntegrityError

    @abc.abstractmethod
    def build(self) -> Path:
        raise NotImplementedError
