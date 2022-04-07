from typing import Set
from peewee import DoesNotExist
from entities.DomainName import DomainName
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_domain_name, helper_zone
from persistence.BaseModel import NameServerEntity, DomainNameEntity, ZoneComposedAssociation, ZoneEntity, \
    AccessAssociation, IpAddressEntity
from utils import domain_name_utils


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


def get_all_from_zone_name(zone_name: str) -> Set[NameServerEntity]:
    zn = domain_name_utils.insert_trailing_point(zone_name)
    try:
        ze = helper_zone.get(zn)
    except DoesNotExist:
        raise
    return get_zone_nameservers(ze)


def get_everyone() -> Set[NameServerEntity]:
    query = NameServerEntity.select()
    result = set()
    for row in query:
        result.add(row)
    return result


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


def get_unresolved() -> Set[NameServerEntity]:
    query = NameServerEntity.select()\
        .join_from(NameServerEntity, DomainNameEntity)\
        .join_from(DomainNameEntity, AccessAssociation)\
        .where(AccessAssociation.ip_address.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
