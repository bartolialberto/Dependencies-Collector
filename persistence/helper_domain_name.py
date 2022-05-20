from typing import Set, Union, Tuple, List
from peewee import DoesNotExist
from entities.DomainName import DomainName
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from entities.paths.APath import APath
from entities.paths.PathBuilder import PathBuilder
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_ip_address, helper_alias
from persistence.BaseModel import DomainNameEntity, IpAddressDependsAssociation, WebSiteEntity, ScriptSiteEntity,\
    IpAddressEntity, WebSiteDomainNameAssociation, ScriptSiteDomainNameAssociation, IpNetworkEntity


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


def __inner_resolve_a_path__(dne: DomainNameEntity, builder=None) -> PathBuilder:
    if builder is None:
        builder = PathBuilder()
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
        builder.add_cname(rr)
    except DoesNotExist:
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
    except DoesNotExist:
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
