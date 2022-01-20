from typing import Set
from peewee import DoesNotExist
from persistence import helper_domain_name
from persistence.BaseModel import DomainNameEntity, IpAddressEntity, AccessAssociation


def insert(dne: DomainNameEntity or None, iae: IpAddressEntity or None) -> AccessAssociation:
    aa, created = AccessAssociation.get_or_create(domain_name=dne, ip_address=iae)
    return aa


def get_of_string_domain_name(domain_name: str) -> Set[AccessAssociation]:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    return get_of_entity_domain_name(dne)


def get_of_entity_domain_name(dne: DomainNameEntity) -> Set[AccessAssociation]:
    result = set()
    query = AccessAssociation.select().where(AccessAssociation.domain_name == dne)
    for row in query:
        result.add(row)
    return result


def delete_of_entity_domain_name(dne: DomainNameEntity) -> None:
    try:
        aas = get_of_entity_domain_name(dne)
    except DoesNotExist:
        return
    for aa in aas:
        aa.delete_instance()
