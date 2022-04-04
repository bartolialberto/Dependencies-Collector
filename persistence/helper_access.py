from typing import Set
from peewee import DoesNotExist
from persistence.BaseModel import DomainNameEntity, IpAddressEntity, AccessAssociation


def insert(dne: DomainNameEntity or None, iae: IpAddressEntity or None) -> AccessAssociation:
    if dne.string == '62.241.4.37.':
        print('', end='')
    elif dne.string == 'mx.cert.legalmail.it.comune.gardonevaltrompia.bs.it.':
        print('', end='')
    aa, created = AccessAssociation.get_or_create(domain_name=dne, ip_address=iae)
    return aa


def get_of_entity_domain_name(dne: DomainNameEntity) -> Set[AccessAssociation]:
    result = set()
    query = AccessAssociation.select()\
        .where((AccessAssociation.domain_name == dne) & (AccessAssociation.ip_address.is_null(False)))
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


def get_unresolved() -> Set[AccessAssociation]:
    result = set()
    query = AccessAssociation.select()\
        .where(AccessAssociation.ip_address.is_null(True))
    for row in query:
        result.add(row)
    return result
