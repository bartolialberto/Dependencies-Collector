from typing import Tuple, Set
from peewee import DoesNotExist
from persistence import helper_domain_name, helper_zone
from persistence.BaseModel import NameServerEntity, DomainNameEntity, ZoneComposedAssociation


def insert(nameserver: str) -> Tuple[NameServerEntity, DomainNameEntity]:
    dne = helper_domain_name.insert(nameserver)
    nse, created = NameServerEntity.get_or_create(name=dne)
    return nse, dne


def get(nameserver: str) -> Tuple[NameServerEntity, DomainNameEntity]:
    try:
        dne = helper_domain_name.get(nameserver)
    except DoesNotExist:
        raise
    try:
        nse = NameServerEntity.get(NameServerEntity.name == dne)
        return nse, dne
    except DoesNotExist:
        raise


def get_from_zone_name(zone_name: str) -> Set[NameServerEntity]:
    try:
        ze = helper_zone.get(zone_name)
    except DoesNotExist:
        raise

    query = NameServerEntity.select()\
        .join_from(NameServerEntity, ZoneComposedAssociation)\
        .where(ZoneComposedAssociation.zone == ze)

    result = set()
    for row in query:
        result.add(row)
    return result
