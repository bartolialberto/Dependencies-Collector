from typing import List, Tuple, Set
from peewee import DoesNotExist
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from exceptions.NoAliasFoundError import NoAliasFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_ip_address, helper_alias, helper_zone
from persistence.BaseModel import DomainNameEntity, IpAddressEntity, DomainNameDependenciesAssociation, ZoneEntity
from utils import domain_name_utils


def insert(name: str) -> DomainNameEntity:
    dn = domain_name_utils.insert_trailing_point(name)
    """
    try:
        domain_name_utils.grammatically_correct(dn)     # TODO: una volta modificato il metodo s-commentare
    except InvalidDomainNameError:
        raise
    """
    dne, created = DomainNameEntity.get_or_create(name=dn)
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
        raise NoAvailablePathError(dne.name)
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
        adnes = helper_alias.get_all_aliases_from_entity(dne)
    except NoAliasFoundError:
        raise NoAvailablePathError(dne.name)
    for adne in adnes:
        try:
            return __inner_resolve_access_path(adne, chain_dne)
        except NoAvailablePathError:
            pass
    raise DoesNotExist


def get_all_that_depends_on_zone(ze: ZoneEntity) -> Set[DomainNameEntity]:
    query = DomainNameDependenciesAssociation.select()\
        .where(DomainNameDependenciesAssociation.zone == ze)
    result = set()
    for row in query:
        result.add(row.domain_name)
    return result

