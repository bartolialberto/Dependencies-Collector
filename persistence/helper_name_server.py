from typing import Set
from peewee import DoesNotExist
from entities.DomainName import DomainName
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_domain_name, helper_zone
from persistence.BaseModel import NameServerEntity, DomainNameEntity, ZoneComposedAssociation, ZoneEntity


def insert(name_server: DomainName) -> NameServerEntity:
    dne = helper_domain_name.insert(name_server)
    nse, created = NameServerEntity.get_or_create(name=dne)
    return nse


def get(name_server: DomainName) -> NameServerEntity:
    try:
        dne = helper_domain_name.get(name_server)
    except DoesNotExist:
        raise
    try:
        nse = NameServerEntity.get(NameServerEntity.name == dne)
        return nse
    except DoesNotExist:
        raise


def get_zone_nameservers(ze: ZoneEntity) -> Set[NameServerEntity]:
    query = NameServerEntity.select()\
        .join_from(NameServerEntity, ZoneComposedAssociation)\
        .where(ZoneComposedAssociation.zone == ze)
    result = set()
    for row in query:
        result.add(row)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result


def get_all_from_zone_name(zone_name: DomainName) -> Set[NameServerEntity]:
    try:
        ze = helper_zone.get(zone_name)
    except DoesNotExist:
        raise
    return get_zone_nameservers(ze)


def filter_domain_names(dnes: Set[DomainNameEntity]) -> Set[NameServerEntity]:
    query = NameServerEntity.select()\
        .where(NameServerEntity.name.in_(dnes))
    result = set()
    for row in query:
        result.add(row)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result
