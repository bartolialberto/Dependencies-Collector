from typing import List
from entities.DomainName import DomainName
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from entities.paths.CNAMEPath import CNAMEPath
from entities.paths.Path import Path
from exceptions.DomainNameNotInPathError import DomainNameNotInPathError
from exceptions.PathIntegrityError import PathIntegrityError
from exceptions.UselessMethodInvocationError import UselessMethodInvocationError


class CNAMEPath():
    def __init__(self, cname_path_list: List[CNAMEPath]):
        if not Path.check_path_integrity(rr_list):
            raise PathIntegrityError
        for rr in rr_list[0:-1]:
            if rr.type != TypesRR.CNAME:
                raise ValueError
        self.path = rr_list

    def get_resolution(self) -> RRecord:
        return self.path[-1]

    def get_aliases_chain(self) -> List[RRecord]:
        return self.path[0:-1]

    def get_canonical_name(self) -> DomainName:
        return self.get_resolution().name

    def get_qname(self) -> DomainName:
        return self.path[0]._second_component_

    def resolve(self, domain_name: DomainName) -> RRecord:
        if self.path[0]._second_component_ == domain_name:
            return self.get_resolution()
        raise DomainNameNotInPathError(domain_name)

    def get_path_from(self, domain_name: DomainName) -> None:
        raise UselessMethodInvocationError

    def __hash__(self):
        return hash(repr(self))