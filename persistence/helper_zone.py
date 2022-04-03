from typing import Set, List, Tuple
from peewee import DoesNotExist
from entities.DomainName import DomainName
from entities.RRecord import RRecord
from entities.Zone import Zone
from entities.enums.TypesRR import TypesRR
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_name_server, helper_ip_address, helper_zone_composed, helper_access, helper_alias, \
    helper_domain_name, helper_alias_to_zone, helper_paths
from persistence.BaseModel import ZoneEntity, DomainNameDependenciesAssociation, ZoneLinksAssociation, \
    DirectZoneAssociation, NameServerEntity, ZoneComposedAssociation, DomainNameEntity
from utils import domain_name_utils


def insert(zone_name: DomainName) -> ZoneEntity:
    ze, created = ZoneEntity.get_or_create(name=zone_name.string)
    return ze


def insert_zone_object(zone: Zone) -> ZoneEntity:
    cname_chain, ze, nses = helper_paths.insert_ns_path(zone.name_path)
    for name_server_a_path in zone.name_servers:
        helper_paths.insert_a_path(name_server_a_path)
    return ze


def get(zone_name: DomainName) -> ZoneEntity:
    try:
        ze = ZoneEntity.get_by_id(zone_name.string)
    except DoesNotExist:
        raise
    return ze


def resolve_zone_object(zone_name: str) -> Tuple[Zone, List[DomainNameEntity]]:
    zn = domain_name_utils.standardize_for_application(zone_name)
    try:
        ze = get(zn)
        dnes = list()
    except DoesNotExist:
        try:
            dne = helper_domain_name.get(zn)
        except DoesNotExist:
            raise
        try:
            ze, dnes = __inner_resolve_zone_from_path(dne, None)
        except DoesNotExist:
            raise
    zo = get_zone_object_from_zone_entity(ze)
    if len(dnes) >= 1:
        name_path = list(map(lambda dne: dne._second_component_, dnes))
        name_path.append(zo.name)
        zo.zone_aliases = RRecord.construct_cname_rrs_from_list_access_path(name_path)
    else:
        dnes = list()
    return zo, dnes


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


# TODO: TEST ULTERIORI
def get_zone_object_from_zone_entity(ze: ZoneEntity) -> Zone:
    try:
        nses = helper_name_server.get_all_from_zone_name(ze.name)
    except DoesNotExist:
        raise
    zone_name = ze.name
    zone_name_servers = list(map(lambda nse: nse._second_component_._second_component_, nses))
    zone_name_aliases = list()
    zone_name_addresses = list()
    for nse in nses:
        try:
            iaes, chain_dnes = helper_domain_name.resolve_access_path(nse.name, get_only_first_address=False)
        except (DoesNotExist, NoAvailablePathError):
            continue        # TODO
        prev = nse.name._second_component_
        for a_dne in chain_dnes[1:]:
            zone_name_aliases.append(RRecord(prev, TypesRR.CNAME, a_dne.string))
            prev = a_dne.string
        ip_addresses = list(map(lambda iae: iae.exploded_notation, iaes))
        zone_name_addresses.append(RRecord(nse.name._second_component_, TypesRR.A, ip_addresses))
    return Zone(zone_name, zone_name_servers, zone_name_aliases, zone_name_addresses, list())


def get_zone_object_from_zone_name(zone_name: str) -> Zone:
    zn = domain_name_utils.standardize_for_application(zone_name)
    try:
        ze = get(zn)
    except DoesNotExist:
        raise
    return get_zone_object_from_zone_entity(ze)


def get_all_of_string_name_server(name_server: str) -> Set[ZoneEntity]:
    try:
        nse, ns_dne = helper_name_server.get(name_server)
    except DoesNotExist:
        raise
    return get_all_of_entity_name_server(nse)


def get_all_of_entity_name_server(nse: NameServerEntity) -> Set[ZoneEntity]:
    query = ZoneComposedAssociation.select()\
        .where(ZoneComposedAssociation.name_server == nse)
    result = set()
    for row in query:
        result.add(row.zone)
    return result


def get_everyone_that_is_direct_zone() -> Set[ZoneEntity]:
    result = set()
    query = DirectZoneAssociation.select()
    for row in query:
        result.add(row.zone)
    return result


def get_everyone() -> Set[ZoneEntity]:
    result = set()
    query = ZoneEntity.select()
    for row in query:
        result.add(row)
    return result


def get_zone_dependencies_of_string_name_server(name_server: str) -> Set[ZoneEntity]:
    try:
        nse, dne = helper_name_server.get(name_server)
    except DoesNotExist:
        raise
    return get_zone_dependencies_of_entity_domain_name(dne)


def get_zone_dependencies_of_string_domain_name(domain_name: str) -> Set[ZoneEntity]:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    return get_zone_dependencies_of_entity_domain_name(dne)


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


def get_direct_zone_object_of(domain_name_param: DomainNameEntity or DomainName or str) -> Zone:
    if isinstance(domain_name_param, DomainNameEntity):
        dne = domain_name_param
    elif isinstance(domain_name_param, DomainName):
        try:
            dne = helper_domain_name.get(domain_name_param)
        except DoesNotExist:
            raise
    else:
        try:
            dne = helper_domain_name.get(DomainName(domain_name_param))
        except DoesNotExist:
            raise
    try:
        dza = DirectZoneAssociation.get((DirectZoneAssociation.domain_name == dne) & (DirectZoneAssociation.zone.is_null(False)))
    except DoesNotExist:
        raise
    return get_zone_object_from_zone_name(dza.zone.name)


def get_direct_zone_of(domain_name_param: DomainNameEntity or str) -> ZoneEntity:
    if isinstance(domain_name_param, DomainNameEntity):
        dne = domain_name_param
    else:
        try:
            dne = helper_domain_name.get(domain_name_param)
        except DoesNotExist:
            raise
    try:
        dza = DirectZoneAssociation.get((DirectZoneAssociation.domain_name == dne) & (DirectZoneAssociation.zone.is_null(False)))
    except DoesNotExist:
        raise
    return dza.zone
