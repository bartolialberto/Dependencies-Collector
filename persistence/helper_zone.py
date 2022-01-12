from typing import Set, Tuple, List
from peewee import DoesNotExist
from entities.Zone import Zone
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_name_server, helper_ip_address, helper_zone_composed, helper_access, helper_alias, \
    helper_domain_name
from persistence.BaseModel import ZoneEntity, DomainNameDependenciesAssociation, NameServerEntity, DomainNameEntity


def insert(name: str) -> ZoneEntity:
    ze, created = ZoneEntity.get_or_create(name=name)
    return ze


def insert_zone_object(zone: Zone) -> ZoneEntity:
    ze, created = ZoneEntity.get_or_create(name=zone.name)
    if created:
        pass
    else:
        return ze       # scorciatoia?

    for nameserver in zone.nameservers:
        nse, nsdne = helper_name_server.insert(nameserver)
        helper_zone_composed.insert(ze, nse)
        try:
            rr = zone.resolve_nameserver(nameserver)
            for value in rr.values:
                iae = helper_ip_address.insert(value)
                helper_access.insert(nsdne, iae)            # TODO: controllare che www.youtube.com abbia più IP collegati
        except NoAvailablePathError:
            raise

    for rr_alias in zone.aliases:
        # get???
        # ne = helper_domain_name.insert(rr_alias.name)
        dne, ne = helper_name_server.insert(rr_alias.name)
        for alias in rr_alias.values:
            ane = helper_domain_name.insert(alias)
            helper_alias.insert(ne, ane)

    return ze


def get_zone_object(zone_name: str) -> Zone:
    pass


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
    query = DomainNameDependenciesAssociation.select()\
        .join_from(DomainNameDependenciesAssociation, ZoneEntity)\
        .where(DomainNameDependenciesAssociation.domain_name == dne)
    for row in query:
        result.add(row.zone)
    return result
