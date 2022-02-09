from typing import List, Tuple, Set
from peewee import DoesNotExist
from exceptions.NoAliasFoundError import NoAliasFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_ip_address, helper_alias, helper_web_site_domain_name, helper_script_site_domain_name
from persistence.BaseModel import DomainNameEntity, IpAddressEntity, DomainNameDependenciesAssociation, ZoneEntity, \
    AutonomousSystemEntity, AccessAssociation, IpAddressDependsAssociation, NetworkNumbersAssociation, WebSiteEntity, \
    ScriptSiteEntity, DirectZoneAssociation
from utils import domain_name_utils


def insert(name: str) -> DomainNameEntity:
    dn = domain_name_utils.insert_trailing_point(name)
    dne, created = DomainNameEntity.get_or_create(string=dn)
    return dne


def get(domain_name: str) -> DomainNameEntity:
    dn = domain_name_utils.insert_trailing_point(domain_name)
    try:
        return DomainNameEntity.get_by_id(dn)
    except DoesNotExist:
        raise


def resolve_access_path(domain_name_parameter: DomainNameEntity or str, get_only_first_address=False) -> Tuple[IpAddressEntity or Set[IpAddressEntity], List[DomainNameEntity]]:
    dne = None
    if isinstance(domain_name_parameter, DomainNameEntity):
        dne = domain_name_parameter
    else:
        try:
            dne = get(domain_name_parameter)
        except DoesNotExist:
            raise
    try:
        inner_result = __inner_resolve_access_path(dne)
    except NoAvailablePathError:
        raise
    if len(inner_result[0]) == 0:
        raise NoAvailablePathError(dne.string)
    if get_only_first_address:
        return inner_result[0].pop(), inner_result[1]
    else:
        return inner_result


def __inner_resolve_access_path(dne: DomainNameEntity, chain_dne=None) -> Tuple[Set[IpAddressEntity], List[DomainNameEntity]]:
    if chain_dne is None:
        chain_dne = list()
    else:
        pass
    chain_dne.append(dne)
    try:
        iaes = helper_ip_address.get_all_of(dne)
        if len(iaes) != 0:
            return iaes, chain_dne
    except DoesNotExist:
        pass
    try:
        adne = helper_alias.get_alias_from_entity(dne)
    except NoAliasFoundError:
        raise NoAvailablePathError(dne.string)
    try:
        return __inner_resolve_access_path(adne, chain_dne)
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
