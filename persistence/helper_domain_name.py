from typing import Set, Union, Tuple, List
from peewee import DoesNotExist
from entities.DomainName import DomainName
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from entities.paths.APath import APath
from entities.paths.builders.APathBuilder import APathBuilder
from exceptions.NoAliasFoundError import NoAliasFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_ip_address, helper_alias, helper_web_site_domain_name, helper_script_site_domain_name
from persistence.BaseModel import DomainNameEntity, DomainNameDependenciesAssociation, ZoneEntity, \
    AutonomousSystemEntity, AccessAssociation, IpAddressDependsAssociation, NetworkNumbersAssociation, WebSiteEntity, \
    ScriptSiteEntity, DirectZoneAssociation, IpAddressEntity, ScriptServerEntity, WebServerEntity, \
    WebSiteDomainNameAssociation, ScriptSiteDomainNameAssociation, IpNetworkEntity


def insert(domain_name: DomainName) -> DomainNameEntity:
    dne, created = DomainNameEntity.get_or_create(string=domain_name.string)
    return dne


def get(domain_name: DomainName) -> DomainNameEntity:
    try:
        return DomainNameEntity.get_by_id(domain_name.string)
    except DoesNotExist:
        raise


def resolve_a_path(dne: DomainNameEntity, as_persistence_entities=False) -> Union[APath, Tuple[List[DomainNameEntity], Set[IpAddressEntity]]]:
    if as_persistence_entities:
        try:
            return __inner_resolve_a_path_as_persistence_entities__(dne, chain=None)
        except NoAvailablePathError:
            raise
    else:
        try:
            a_path_builder = __inner_resolve_a_path__(dne, builder=None)
        except NoAvailablePathError:
            raise
        return a_path_builder.build()


def __inner_resolve_a_path__(dne: DomainNameEntity, builder=None) -> APathBuilder:
    if builder is None:
        builder = APathBuilder()
    else:
        pass
    try:
        iaes = helper_ip_address.get_all_of(dne)
        rr = RRecord(DomainName(dne.string), TypesRR.A, list(map(lambda iae: iae.exploded_notation, iaes)))
        builder.complete_resolution(rr)
        return builder
    except NoDisposableRowsError:
        pass
    try:
        adne = helper_alias.get_alias_from_entity(dne)
        rr = RRecord(DomainName(dne.string), TypesRR.CNAME, [adne.string])
        builder.add_alias(rr)
    except NoAliasFoundError:
        raise NoAvailablePathError(dne.string)
    try:
        return __inner_resolve_a_path__(adne, builder)
    except NoAvailablePathError:
        raise


def __inner_resolve_a_path_as_persistence_entities__(dne: DomainNameEntity, chain=None) -> Tuple[List[DomainNameEntity], Set[IpAddressEntity]]:
    if chain is None:
        chain = list()
    else:
        pass
    chain.append(dne)
    try:
        iaes = helper_ip_address.get_all_of(dne)
        return chain, iaes
    except NoDisposableRowsError:
        pass
    try:
        adne = helper_alias.get_alias_from_entity(dne)
    except NoAliasFoundError:
        raise NoAvailablePathError(dne.string)
    try:
        return __inner_resolve_a_path_as_persistence_entities__(adne, chain)
    except NoAvailablePathError:
        raise


def get_of(site: Union[WebSiteEntity, ScriptSiteEntity]) -> DomainNameEntity:
    if isinstance(site, WebSiteEntity):
        try:
            wsdna = WebSiteDomainNameAssociation.get(WebSiteDomainNameAssociation.web_site == site)
            return wsdna.domain_name
        except DoesNotExist:
            raise
    else:
        try:
            ssdna = ScriptSiteDomainNameAssociation.get(ScriptSiteDomainNameAssociation.script_site == site)
            return ssdna.domain_name
        except DoesNotExist:
            raise


def get_all_that_depends_on_zone(ze: ZoneEntity) -> Set[DomainNameEntity]:
    query = DomainNameDependenciesAssociation.select()\
        .where(DomainNameDependenciesAssociation.zone == ze)
    result = set()
    for row in query:
        result.add(row.domain_name)
    return result


def get_everyone_from_ip_network(ine: IpNetworkEntity) -> Set[DomainNameEntity]:
    iaes = set()
    query = IpAddressDependsAssociation.select() \
        .where(IpAddressDependsAssociation.ip_network == ine)
    for row in query:
        iaes.add(row.ip_address)
    if len(iaes) == 0:
        raise NoDisposableRowsError
    result = set()
    for iae in iaes:
        try:
            current_dnes = helper_ip_address.resolve_reversed_a_path(iae)
            result.add(current_dnes[0])
        except NoAvailablePathError:
            pass
    if len(iaes) == 0:
        raise NoDisposableRowsError
    else:
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
