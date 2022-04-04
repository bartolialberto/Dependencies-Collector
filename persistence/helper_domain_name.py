from typing import Set
from peewee import DoesNotExist
from entities.DomainName import DomainName
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from entities.paths.APath import APath
from entities.paths.builders.APathBuilder import APathBuilder
from exceptions.NoAliasFoundError import NoAliasFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_ip_address, helper_alias, helper_web_site_domain_name, helper_script_site_domain_name
from persistence.BaseModel import DomainNameEntity, DomainNameDependenciesAssociation, ZoneEntity, \
    AutonomousSystemEntity, AccessAssociation, IpAddressDependsAssociation, NetworkNumbersAssociation, WebSiteEntity, \
    ScriptSiteEntity, DirectZoneAssociation


def insert(domain_name: DomainName) -> DomainNameEntity:
    dne, created = DomainNameEntity.get_or_create(string=domain_name.string)
    return dne


def get(domain_name: DomainName) -> DomainNameEntity:
    try:
        return DomainNameEntity.get_by_id(domain_name.string)
    except DoesNotExist:
        raise


def resolve_access_path(domain_name_parameter: DomainNameEntity or str) -> APath:
    dne = None
    if isinstance(domain_name_parameter, DomainNameEntity):
        dne = domain_name_parameter
    else:
        try:
            dne = get(domain_name_parameter)
        except DoesNotExist:
            raise
    try:
        a_path_builder = __inner_resolve_access_path(dne)
    except NoAvailablePathError:
        raise
    return a_path_builder.build()


def __inner_resolve_access_path(dne: DomainNameEntity, builder=None) -> APathBuilder:
    if builder is None:
        builder = APathBuilder()
    else:
        pass
    try:
        iaes = helper_ip_address.get_all_of(dne)
        if len(iaes) != 0:
            rr = RRecord(DomainName(dne.string), TypesRR.A, list(map(lambda iae: iae.exploded_notation, iaes)))
            builder.complete_resolution(rr)
            return builder
    except DoesNotExist:
        pass
    try:
        adne = helper_alias.get_alias_from_entity(dne)
        rr = RRecord(DomainName(dne.string), TypesRR.CNAME, [adne.string])
        builder.add_alias(rr)
    except NoAliasFoundError:
        raise NoAvailablePathError(dne.string)
    try:
        return __inner_resolve_access_path(adne, builder)
    except NoAvailablePathError:
        raise


def get_all_that_depends_on_zone(ze: ZoneEntity) -> Set[DomainNameEntity]:
    query = DomainNameDependenciesAssociation.select()\
        .where(DomainNameDependenciesAssociation.zone == ze)
    result = set()
    for row in query:
        result.add(row.domain_name)
    return result


def get_all_from_entity_autonomous_system(ase: AutonomousSystemEntity) -> Set[DomainNameEntity]:
    query = AccessAssociation.select() \
        .join(IpAddressDependsAssociation, on=(AccessAssociation.ip_address == IpAddressDependsAssociation.ip_address)) \
        .join(NetworkNumbersAssociation, on=(IpAddressDependsAssociation.ip_range_tsv == NetworkNumbersAssociation.ip_range_tsv))\
        .where(NetworkNumbersAssociation.autonomous_system == ase)
    result = set()
    for row in query:
        result.add(row.domain_name)
    return result


def get_from_entity_web_site(wse: WebSiteEntity) -> DomainNameEntity:
    try:
        wsdna = helper_web_site_domain_name.get_from_entity_web_site(wse)
    except DoesNotExist:
        raise
    return wsdna.domain_name


def get_from_entity_script_site(sse: ScriptSiteEntity) -> DomainNameEntity:
    try:
        ssdna = helper_script_site_domain_name.get_from_entity_script_site(sse)
    except DoesNotExist:
        raise
    return ssdna.domain_name


def get_from_direct_zone(ze: ZoneEntity) -> Set[DomainNameEntity]:
    query = DirectZoneAssociation.select()\
        .where(DirectZoneAssociation.zone == ze)
    result = set()
    for row in query:
        result.add(row.domain_name)
    return result


def get_everyone() -> Set[DomainNameEntity]:
    query = DomainNameEntity.select()
    result = set()
    for row in query:
        result.add(row)
    return result
