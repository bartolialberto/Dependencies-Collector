from typing import Set
from persistence.BaseModel import DomainNameEntity, IpAddressEntity, AccessAssociation


def insert(dne: DomainNameEntity or None, iae: IpAddressEntity or None) -> AccessAssociation:
    aa, created = AccessAssociation.get_or_create(domain_name=dne, ip_address=iae)
    return aa


def get_of_entity_domain_name(dne: DomainNameEntity) -> Set[AccessAssociation]:
    result = set()
    query = AccessAssociation.select()\
        .where((AccessAssociation.domain_name == dne) & (AccessAssociation.ip_address.is_null(False)))
    for row in query:
        result.add(row)
    return result


def get_unresolved() -> Set[AccessAssociation]:
    result = set()
    query = AccessAssociation.select()\
        .where(AccessAssociation.ip_address.is_null(True))
    for row in query:
        result.add(row)
    return result
