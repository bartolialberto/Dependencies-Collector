import abc
from utils import resource_records_utils
from abc import ABC
from typing import List
from entities.DomainName import DomainName
from entities.RRecord import RRecord


class Path(ABC):
    @abc.abstractmethod
    def get_resolution(self) -> RRecord:
        pass

    @abc.abstractmethod
    def get_aliases_chain(self) -> List[RRecord]:
        pass

    @abc.abstractmethod
    def get_canonical_name(self) -> DomainName:
        pass

    @abc.abstractmethod
    def get_qname(self) -> DomainName:
        pass

    @abc.abstractmethod
    def get_list(self) -> List[RRecord]:
        pass

    @abc.abstractmethod
    def resolve(self, domain_name: DomainName) -> RRecord:
        pass

    def stamp(self) -> str:
        result = ''
        if len(self.get_aliases_chain()) == 0:
            result = result + str(self.get_resolution().name)
        else:
            for i, rr in enumerate(self.get_aliases_chain()):
                if i == 0:
                    result = str(rr.name) + " --CNAME-> " + rr.get_first_value().string
                else:
                    result = result + " --CNAME--> " + rr.get_first_value().string
        # return result + " ==> " + str(self.get_resolution().values)
        if len(self.get_aliases_chain()) == 0:
            return self.get_resolution().name.string + " =="+self.get_resolution().type.to_string()+"=> " + resource_records_utils.stamp_values(self.get_resolution().type, self.get_resolution().values)
        else:
            return result + " =="+self.get_resolution().type.to_string()+"=> " + resource_records_utils.stamp_values(self.get_resolution().type, self.get_resolution().values)

    def __str__(self) -> str:
        return self.stamp()

    def __eq__(self, other) -> bool:
        if isinstance(other, Path):
            return self.get_resolution() == other.get_resolution() and self.get_qname() == other.get_qname()
        else:
            return False

    def __hash__(self) -> int:
        return hash((self.get_resolution(), self.get_qname()))

    @staticmethod
    def check_path_integrity(path: List[RRecord]) -> bool:
        if len(path) == 0:
            return False
        elif len(path) == 1:
            return True
        else:
            prev_alias = path[0].get_first_value()
            for rr in path[1:]:
                if rr.name != prev_alias:
                    return False
                prev_alias = rr.get_first_value()
            return True
