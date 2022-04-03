from typing import Tuple, Set, List
from peewee import DoesNotExist

from entities.DomainName import DomainName
from exceptions.EmptyResultError import EmptyResultError
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_domain_name, helper_zone, helper_ip_address
from persistence.BaseModel import NameServerEntity, DomainNameEntity, ZoneComposedAssociation, ZoneEntity, \
    AccessAssociation, IpAddressEntity
from utils import domain_name_utils


def insert(name_server: DomainName) -> NameServerEntity:
    dne = helper_domain_name.insert(name_server)
    nse, created = NameServerEntity.get_or_create(name=dne)
    return nse, dne


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


def get_all_from_zone_entity(ze: ZoneEntity) -> Set[NameServerEntity]:
    query = NameServerEntity.select()\
        .join_from(NameServerEntity, ZoneComposedAssociation)\
        .where(ZoneComposedAssociation.zone == ze)

    result = set()
    for row in query:
        result.add(row)
    return result


def get_all_from_zone_name(zone_name: str) -> Set[NameServerEntity]:
    zn = domain_name_utils.insert_trailing_point(zone_name)
    try:
        ze = helper_zone.get(zn)
    except DoesNotExist:
        raise
    return get_all_from_zone_entity(ze)


def get_all_from_ip_address(address: str) -> List[NameServerEntity]:
    try:
        iae = helper_ip_address.get(address)
    except DoesNotExist:
        raise
    query = AccessAssociation.select()\
        .join_from(AccessAssociation, DomainNameEntity)\
        .join_from(DomainNameEntity, NameServerEntity)\
        .where(AccessAssociation.ip_address == iae)
    result = list()
    for row in query:
        result.append(row.domain_name)
    if len(result) == 0:
        raise EmptyResultError
    else:
        return result


def get_everyone() -> Set[NameServerEntity]:
    query = NameServerEntity.select()
    result = set()
    for row in query:
        result.add(row)
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
