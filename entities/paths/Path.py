import abc
from utils import resource_records_utils
from abc import ABC
from typing import List, Union
from entities.DomainName import DomainName
from entities.RRecord import RRecord


class Path(ABC):
    @property
    @abc.abstractmethod
    def path(self) -> List[RRecord]:
        raise NotImplementedError

    @path.setter
    @abc.abstractmethod
    def path(self, new_val: List[RRecord]) -> List[RRecord]:
        raise NotImplementedError

    def get_resolution(self) -> RRecord:
        return self.path[-1]

    def get_aliases_chain(self, as_resource_records=True) -> Union[List[RRecord], List[DomainName]]:
        if as_resource_records:
            return self.path[0:-1]
        else:
            result = list()
            result.append(self.path[0].name)
            for rr in self.path[0:-1]:
                result.append(rr.get_first_value())
            return result

    def get_canonical_name(self) -> DomainName:
        return self.get_resolution().name

    def get_qname(self) -> DomainName:
        return self.path[0].name

    @abc.abstractmethod
    def resolve(self, domain_name: DomainName) -> RRecord:
        raise NotImplementedError

    def stamp(self) -> str:
        result = ''
        if len(self.get_aliases_chain()) == 0:
            result = result + str(self.get_resolution().name)
        else:
            for i, rr in enumerate(self.get_aliases_chain()):
                if i == 0:
                    result = str(rr.name) + " --CNAME-> " + rr.get_first_value().string
                else:
                    result = result + " --CNAME-> " + rr.get_first_value().string
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

    def __iter__(self):
        return self.path.__iter__()

    def __next__(self):
        return self.path.__iter__().__next__()

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
