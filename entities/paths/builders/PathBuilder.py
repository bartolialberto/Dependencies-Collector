import abc
from entities.paths.Path import Path
from entities.RRecord import RRecord


class PathBuilder(abc.ABC):
    @abc.abstractmethod
    def complete_resolution(self, rr: RRecord) -> 'PathBuilder':        # FORWARD DECLARATIONS (REFERENCES)
        pass

    @abc.abstractmethod
    def add_alias(self, rr: RRecord) -> 'PathBuilder':      # FORWARD DECLARATIONS (REFERENCES)
        pass

    @abc.abstractmethod
    def build(self) -> Path:
        pass
