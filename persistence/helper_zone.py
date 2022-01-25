import copy
from typing import Set
from peewee import DoesNotExist
from entities.RRecord import RRecord
from entities.Zone import Zone
from entities.enums.TypesRR import TypesRR
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_name_server, helper_ip_address, helper_zone_composed, helper_access, helper_alias, \
    helper_domain_name
from persistence.BaseModel import ZoneEntity, DomainNameDependenciesAssociation, ZoneLinksAssociation, \
    DirectZoneAssociation
from utils import domain_name_utils


def insert(zone_name: str) -> ZoneEntity:
    zn = domain_name_utils.insert_trailing_point(zone_name)
    ze, created = ZoneEntity.get_or_create(name=zn)
    return ze


def insert_zone_object(zone: Zone) -> ZoneEntity:
    ze, created = ZoneEntity.get_or_create(name=zone.name)
    if created:
        pass
    else:
        return ze       # scorciatoia?

    nsdne_dict = dict()
    for nameserver in zone.nameservers:
        nse, nsdne = helper_name_server.insert(nameserver)
        helper_zone_composed.insert(ze, nse)
        nsdne_dict[nameserver] = nsdne  # to avoid get again entities from database

    for rr_alias in zone.aliases:
        dne = helper_domain_name.insert(rr_alias.name)
        for alias in rr_alias.values:
            ane = helper_domain_name.insert(alias)
            helper_alias.insert(dne, ane)

    name_server_unresolved = set(copy.deepcopy(zone.nameservers))
    for rr in zone.addresses:
        dne = helper_domain_name.insert(rr.name)
        last_ip_string = None
        for value in rr.values:
            iae = helper_ip_address.insert(value)
            helper_access.insert(dne, iae)
            last_ip_string = value
        try:
            name_server_to_be_removed = zone.is_ip_of_name_servers(last_ip_string)
        except ValueError:
            raise
        name_server_unresolved.remove(name_server_to_be_removed)



    for name_server in name_server_unresolved:
        helper_access.insert(nsdne_dict[name_server], None)

    return ze


def get_zone_object(zone_name: str) -> Zone:
    try:
        ze = get(zone_name)
    except DoesNotExist:
        raise
    try:
        nses = helper_name_server.get_all_from_zone_name(ze.name)
    except DoesNotExist:
        raise
    zone_name_servers = list(map(lambda nse: nse.name.name, nses))
    zone_name_aliases = list()
    zone_name_addresses = list()
    for nse in nses:
        try:
            iae = helper_ip_address.get_first_of(nse.name.name)
            zone_name_addresses.append(RRecord(nse.name.name, TypesRR.A, iae.exploded_notation))
        except DoesNotExist:
            try:
                iae, a_dnes = helper_domain_name.resolve_access_path(nse.name, get_only_first_address=True)
            except NoAvailablePathError:
                raise
            prev = nse.name.name
            for a_dne in a_dnes:
                zone_name_aliases.append(RRecord(prev, TypesRR.CNAME, a_dne.name))
                prev = a_dne.name
            zone_name_addresses.append(RRecord(nse.name.name, TypesRR.A, iae.exploded_notation))
    return Zone(zone_name, zone_name_servers, zone_name_aliases, zone_name_addresses)


def get(zone_name: str) -> ZoneEntity:
    zn = domain_name_utils.insert_trailing_point(zone_name)
    try:
        ze = ZoneEntity.get_by_id(zn)
    except DoesNotExist:
        raise
    return ze


def get_all() -> Set[ZoneEntity]:
    result = set()
    query = ZoneEntity.select()
    for row in query:
        result.add(row)
    return result


def get_zone_dependencies_of_domain_name(domain_name: str) -> Set[ZoneEntity]:
    dn = domain_name_utils.insert_trailing_point(domain_name)
    try:
        dne = helper_domain_name.get(dn)
    except DoesNotExist:
        raise
    result = set()
    query = DomainNameDependenciesAssociation.select()\
        .join_from(DomainNameDependenciesAssociation, ZoneEntity)\
        .where(DomainNameDependenciesAssociation.domain_name == dne)
    for row in query:
        result.add(row.zone)
    return result


def get_zone_dependencies_of_zone(zone_name: str) -> Set[ZoneEntity]:
    zn = domain_name_utils.insert_trailing_point(zone_name)
    try:
        ze = get(zn)
    except DoesNotExist:
        raise
    result = set()
    query = ZoneLinksAssociation.select()\
        .join(ZoneEntity, on=(ZoneLinksAssociation.dependency == ze))
    for row in query:
        result.add(row.zone)
    return result


def get_direct_zone_object_of(domain_name: str) -> Zone:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    try:
        dza = DirectZoneAssociation.get(DirectZoneAssociation.domain_name == dne)
    except DoesNotExist:
        raise
    return get_zone_object(dza.zone.name)
