from typing import Tuple, Set, List
from peewee import DoesNotExist
from exceptions.EmptyResultError import EmptyResultError
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_domain_name, helper_zone, helper_ip_address
from persistence.BaseModel import NameServerEntity, DomainNameEntity, ZoneComposedAssociation, ZoneEntity, \
    AccessAssociation, IpAddressEntity
from utils import domain_name_utils


def insert(name_server: str) -> Tuple[NameServerEntity, DomainNameEntity]:
    ns = domain_name_utils.insert_trailing_point(name_server)
    dne = helper_domain_name.insert(ns)
    nse, created = NameServerEntity.get_or_create(name=dne)
    return nse, dne


def get(name_server: str) -> Tuple[NameServerEntity, DomainNameEntity]:
    try:
        dne = helper_domain_name.get(name_server)
    except DoesNotExist:
        raise
    try:
        nse = NameServerEntity.get(NameServerEntity.name == dne)
        return nse, dne
    except DoesNotExist:
        raise


def get_all_from_zone_name(zone_name: str) -> Set[NameServerEntity]:
    zn = domain_name_utils.insert_trailing_point(zone_name)
    try:
        ze = helper_zone.get(zn)
    except DoesNotExist:
        raise

    query = NameServerEntity.select()\
        .join_from(NameServerEntity, ZoneComposedAssociation)\
        .where(ZoneComposedAssociation.zone == ze)

    result = set()
    for row in query:
        result.add(row)
    return result


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


def get_unresolved() -> Set[NameServerEntity]:
    query = NameServerEntity.select()\
        .join_from(NameServerEntity, DomainNameEntity)\
        .join_from(DomainNameEntity, AccessAssociation)\
        .where(AccessAssociation.ip_address.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
