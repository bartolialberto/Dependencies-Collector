from typing import List
from entities.DomainName import DomainName
from entities.paths.Path import Path
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.DomainNameNotInPathError import DomainNameNotInPathError
from exceptions.PathIntegrityError import PathIntegrityError


class CNAMEPath(Path):
    def __init__(self, rr_list: List[RRecord]):
        if not Path.check_path_integrity(rr_list):
            raise PathIntegrityError
        for rr in rr_list:
            if rr.type != TypesRR.CNAME:
                raise ValueError
        self.__path = rr_list

    @property
    def path(self) -> List[RRecord]:
        return self.__path

    def resolve(self, domain_name: DomainName) -> RRecord:
        for rr in self.path:
            if rr.name == domain_name:
                return self.get_resolution()
        if self.get_resolution().name == domain_name:
            return self.get_resolution()
        raise DomainNameNotInPathError(domain_name)
