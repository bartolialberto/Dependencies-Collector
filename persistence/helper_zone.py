from typing import Set
from peewee import DoesNotExist
from entities.Zone import Zone
from persistence import helper_nameserver, helper_ip_address, helper_zone_composed, helper_access, helper_alias, \
    helper_domain_name
from persistence.BaseModel import ZoneEntity, NameDependenciesAssociation


def insert(name: str) -> ZoneEntity:
    ze, created = ZoneEntity.get_or_create(name=name)
    return ze


def insert_zone_object(zone: Zone):
    ze, created = ZoneEntity.get_or_create(name=zone.name)
    if created:
        pass
    else:
        return ze       # scorciatoia?

    for rr_nameserver in zone.nameservers:
        nse, nsdne = helper_nameserver.insert(rr_nameserver.name)
        helper_zone_composed.insert(ze, nse)
        iae = helper_ip_address.insert(rr_nameserver.get_first_value())
        helper_access.insert(nsdne, iae)

    for rr_alias in zone.aliases:
        # get???
        # ne = helper_domain_name.insert(rr_alias.name)
        dne, ne = helper_nameserver.insert(rr_alias.name)
        for alias in rr_alias.values:
            ane = helper_domain_name.insert(alias)
            helper_alias.insert(ne, ane)

    return ze


def get_zone_object(zone_name: str) -> Zone:
    try:
        ze = get(zone_name)
    except DoesNotExist:
        raise
    try:
        nss = helper_nameserver.get_from_zone_name(zone_name)
    except DoesNotExist:
        raise
    result_zone_name = zone_name
    result_nameservers = list()
    result_aliases = list()
    for ns in nss:
        try:
            aliases = helper_alias.get_all_aliases_from_name(ns.name)
        except DoesNotExist:
            pass
    Zone()


def get(zone_name: str) -> ZoneEntity:
    try:
        ze = ZoneEntity.get_by_id(zone_name)
    except DoesNotExist:
        raise
    return ze


def get_all() -> Set[ZoneEntity]:
    result = set()
    query = ZoneEntity.select()
    for row in query:
        result.add(row)
    return result


def get_zone_dependencies_of(domain_name: str) -> Set[ZoneEntity]:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    result = set()
    query = NameDependenciesAssociation.select()\
        .join_from(NameDependenciesAssociation, ZoneEntity)\
        .where(NameDependenciesAssociation.domain_name == dne)
    for row in query:
        result.add(row.zone)
    return result
