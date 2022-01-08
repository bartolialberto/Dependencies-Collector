from typing import Set
from peewee import DoesNotExist
from persistence import helper_zone
from persistence.BaseModel import ZoneEntity, ZoneLinksAssociation


def insert(ze: ZoneEntity, ze_dep: ZoneEntity) -> ZoneLinksAssociation:
    zla, created = ZoneLinksAssociation.get_or_create(zone=ze, dependency=ze_dep)
    return zla


def get_from_zone_name(zone_name: str) -> ZoneEntity:
    try:
        ze = helper_zone.get(zone_name)
    except DoesNotExist:
        raise
    query = ZoneLinksAssociation.select()\
        .join(ZoneEntity, on=(ZoneLinksAssociation.zone == ze))
    for row in query:
        return row.dependency
    raise DoesNotExist


def get_all_from_zone_name(zone_name: str) -> Set[ZoneEntity]:
    try:
        ze = helper_zone.get(zone_name)
    except DoesNotExist:
        raise
    result = set()
    query = ZoneLinksAssociation.select()\
        .join(ZoneEntity, on=(ZoneLinksAssociation.zone == ze))
    for row in query:
        result.add(row.dependency)
    return result
