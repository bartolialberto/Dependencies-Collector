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
    ns = domain_name_utils.insert_trailing_point(name_server)
    try:
        dne = helper_domain_name.get(ns)
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


def get_every_zone_of(name_server_parameter: NameServerEntity or str) -> Set[ZoneEntity]:
    nse = None
    if isinstance(name_server_parameter, NameServerEntity):
        nse = name_server_parameter
    else:
        try:
            nse, dne = get(name_server_parameter)
        except DoesNotExist:
            raise
    result = set()
    query = ZoneComposedAssociation.select()\
        .join_from(ZoneComposedAssociation, ZoneEntity)\
        .where(ZoneComposedAssociation.name_server == nse)
    for row in query:
        result.add(row.zone)
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


def get_first_from_ip_address(address: str) -> NameServerEntity:
    try:
        iae = helper_ip_address.get(address)
    except DoesNotExist:
        raise
    query = AccessAssociation.select()\
        .join_from(AccessAssociation, DomainNameEntity)\
        .join_from(DomainNameEntity, NameServerEntity)\
        .where(AccessAssociation.ip_address == iae)\
        .limit(1)
    for row in query:
        return row.domain_name
    raise DoesNotExist


def resolve_access_path(nse: NameServerEntity, get_only_first_address=False) -> Tuple[IpAddressEntity or Set[IpAddressEntity], List[DomainNameEntity]]:
    try:
        return helper_domain_name.resolve_access_path(nse.name, get_only_first_address=get_only_first_address)
    except NoAvailablePathError:
        raise


def get_unresolved() -> Set[NameServerEntity]:
    query = NameServerEntity.select()\
        .join_from(NameServerEntity, DomainNameEntity)\
        .join_from(DomainNameEntity, AccessAssociation)\
        .where(AccessAssociation.ip_address.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
