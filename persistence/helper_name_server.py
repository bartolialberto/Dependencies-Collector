from typing import Tuple, Set
from peewee import DoesNotExist
from persistence import helper_domain_name, helper_zone
from persistence.BaseModel import NameServerEntity, DomainNameEntity, ZoneComposedAssociation, ZoneEntity
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
