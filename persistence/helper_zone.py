from typing import Set, List, Tuple
from peewee import DoesNotExist
from entities.DomainName import DomainName
from entities.Zone import Zone
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_alias, helper_domain_name, helper_alias_to_zone, helper_paths, helper_access
from persistence.BaseModel import ZoneEntity, DomainNameDependenciesAssociation, ZoneLinksAssociation, \
    DirectZoneAssociation, NameServerEntity, ZoneComposedAssociation, DomainNameEntity


def insert(zone_name: DomainName) -> ZoneEntity:
    ze, created = ZoneEntity.get_or_create(name=zone_name.string)
    return ze


def insert_zone_object(zone: Zone) -> ZoneEntity:
    cname_chain, ze, nses = helper_paths.insert_ns_path(zone.name_path)
    for name_server_a_path in zone.name_servers:
        helper_paths.insert_a_path(name_server_a_path)
    for name_server in zone.unresolved_name_servers.keys():
        name_server_nse = None
        for nse in nses:
            if nse.name.string == name_server.string:
                name_server_nse = nse
        if name_server_nse is None:
            raise ValueError
        else:
            helper_access.insert(name_server_nse.name, None)
    return ze


def get(zone_name: DomainName) -> ZoneEntity:
    try:
        ze = ZoneEntity.get_by_id(zone_name.string)
    except DoesNotExist:
        raise
    return ze


def __inner_resolve_zone_from_path(dne: DomainNameEntity, result: List[DomainNameEntity] or None) -> Tuple[ZoneEntity, List[DomainNameEntity]]:
    if result is None:
        result = list()
    else:
        pass
    result.append(dne)
    try:
        zna = helper_alias_to_zone.get_from_entity_domain_name(dne)
        return zna.zone, result
    except DoesNotExist:
        try:
            alias_dne = helper_alias.get_alias_from_entity(dne)
            return __inner_resolve_zone_from_path(alias_dne, result)
        except DoesNotExist:
            raise


def get_everyone() -> Set[ZoneEntity]:
    result = set()
    query = ZoneEntity.select()
    for row in query:
        result.add(row)
    return result


def get_zone_dependencies_of_domain_name(domain_name: DomainName) -> Set[ZoneEntity]:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    return get_zone_dependencies_of_entity_domain_name(dne)


def get_zone_dependencies_of_entity_domain_name(dne: DomainNameEntity) -> Set[ZoneEntity]:
    result = set()
    query = DomainNameDependenciesAssociation.select()\
        .where(DomainNameDependenciesAssociation.domain_name == dne)
    for row in query:
        result.add(row.zone)
    return result


def get_zone_dependencies_of_zone_name(zone_name: DomainName) -> Set[ZoneEntity]:
    try:
        ze = get(zone_name)
    except DoesNotExist:
        raise
    result = set()
    query = ZoneLinksAssociation.select()\
        .join(ZoneEntity, on=(ZoneLinksAssociation.zone == ze))
    for row in query:
        result.add(row.dependency)
    return result


def get_not_null_direct_zone_of(dne: DomainNameEntity) -> ZoneEntity:
    try:
        dza = DirectZoneAssociation.get((DirectZoneAssociation.domain_name == dne) & (DirectZoneAssociation.zone.is_null(False)))
    except DoesNotExist:
        raise
    return dza.zone


def get_direct_zone_of(dne: DomainNameEntity) -> ZoneEntity:
    try:
        dza = DirectZoneAssociation.get(DirectZoneAssociation.domain_name == dne)
    except DoesNotExist:
        raise
    return dza.zone


def get_entire_zones_from_nameservers_pool(nses_contained_in_a_network: Set[NameServerEntity]) -> Set[ZoneEntity]:
    query = ZoneComposedAssociation.select(ZoneComposedAssociation)\
        .where(ZoneComposedAssociation.name_server.in_(nses_contained_in_a_network))
    result = set()
    ze_nse = dict()
    zes = set()
    for row in query:
        zes.add(row.zone)
        try:
            ze_nse[row.zone].add(row.name_server)
        except KeyError:
            ze_nse[row.zone] = {row.name_server}
    query = ZoneComposedAssociation.select(ZoneComposedAssociation) \
        .where(ZoneComposedAssociation.zone.in_(zes))
    for row in query:
        try:
            ze_nse[row.zone].add(row.name_server)
        except KeyError:
            ze_nse[row.zone] = {row.name_server}
    for ze in ze_nse.keys():
        is_contained = True
        for nse in ze_nse[ze]:
            if nse in nses_contained_in_a_network:
                pass
            else:
                is_contained = False
                break
        if is_contained:
            result.add(ze)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result
