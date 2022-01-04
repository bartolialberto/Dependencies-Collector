from typing import Tuple, Set
from peewee import DoesNotExist
from persistence import helper_domain_name, helper_zone
from persistence.BaseModel import NameserverEntity, DomainNameEntity, ZoneComposedAssociation


def insert(nameserver: str) -> Tuple[NameserverEntity, DomainNameEntity]:
    dne = helper_domain_name.insert(nameserver)
    nse, created = NameserverEntity.get_or_create(name=dne)
    return nse, dne


def get(nameserver: str) -> Tuple[NameserverEntity, DomainNameEntity]:
    try:
        dne = helper_domain_name.get(nameserver)
    except DoesNotExist:
        raise
    try:
        nse = NameserverEntity.get(NameserverEntity.name == dne)
        return nse, dne
    except DoesNotExist:
        raise


def get_from_zone_name(zone_name: str) -> Set[NameserverEntity]:
    try:
        ze = helper_zone.get(zone_name)
    except DoesNotExist:
        raise

    query = NameserverEntity.select()\
        .join_from(NameserverEntity, ZoneComposedAssociation)\
        .where(ZoneComposedAssociation.zone == ze)

    result = set()
    for row in query:
        result.add(row)
    return result
