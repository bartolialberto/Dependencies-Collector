from typing import Set
from peewee import DoesNotExist
from persistence.BaseModel import DomainNameEntity, IpAddressEntity, AccessAssociation


def insert(dne: DomainNameEntity or None, iae: IpAddressEntity or None) -> AccessAssociation:
    aa, created = AccessAssociation.get_or_create(domain_name=dne, ip_address=iae)
    return aa


def get_first_of(dne: DomainNameEntity) -> AccessAssociation:
    try:
        aa = AccessAssociation.get(AccessAssociation.domain_name == dne)
    except DoesNotExist:
        raise
    return aa


def get_all_of(dne: DomainNameEntity) -> Set[AccessAssociation]:
    result = set()
    query = AccessAssociation.select().where(AccessAssociation.domain_name == dne)
    for row in query:
        result.add(row)
    return result
