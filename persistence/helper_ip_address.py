import ipaddress
from typing import Set, List, Union
from peewee import DoesNotExist

from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_domain_name
from persistence.BaseModel import IpAddressEntity, DomainNameEntity, AccessAssociation, IpNetworkEntity, \
    IpAddressDependsAssociation, AliasAssociation


def insert(address_param: Union[str, ipaddress.IPv4Address]) -> IpAddressEntity:
    address = None
    if isinstance(address_param, ipaddress.IPv4Address):
        address = address_param
    else:
        try:
            address = ipaddress.IPv4Address(address_param)
        except ValueError:
            raise
    iae, created = IpAddressEntity.get_or_create(exploded_notation=address.exploded)
    return iae


def get(ip_address: ipaddress.IPv4Address) -> IpAddressEntity:
    try:
        iae = IpAddressEntity.get_by_id(ip_address.exploded)
    except DoesNotExist:
        raise
    return iae


def resolve_reversed_a_path(iae: IpAddressEntity, as_reversed=False) -> List[DomainNameEntity]:
    query = AccessAssociation.select() \
        .where(AccessAssociation.ip_address == iae)
    result = list()
    canonical_dnes = set()
    for row in query:
        canonical_dnes.add(row.domain_name)
    if len(canonical_dnes) == 0:
        raise NoAvailablePathError(iae.exploded_notation)
    for dne in canonical_dnes:
        chain_dnes = __inner_resolve_reversed_a_path__(dne, None)
        for chain_dne in chain_dnes:
            result.append(chain_dne)
    if as_reversed:
        return result
    else:
        return list(reversed(result))


def __inner_resolve_reversed_a_path__(alias_dne: DomainNameEntity, chain: Union[List[DomainNameEntity], None]) -> List[DomainNameEntity]:
    if chain is None:
        chain = list()
    else:
        pass
    chain.append(alias_dne)
    try:
        aa = AliasAssociation.get(AliasAssociation.alias == alias_dne)
        name_dne = aa.name
    except DoesNotExist:
        return chain
    return __inner_resolve_reversed_a_path__(name_dne, chain)


def get_all_of(dne: DomainNameEntity) -> Set[IpAddressEntity]:
    query = AccessAssociation.select()\
        .where((AccessAssociation.domain_name == dne) & (AccessAssociation.ip_address.is_null(False)))
    result = set()
    for row in query:
        result.add(row.ip_address)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result


def get_all_of_entity_network(ine: IpNetworkEntity) -> Set[IpAddressEntity]:
    result = set()
    query = IpAddressDependsAssociation.select()\
        .where(IpAddressDependsAssociation.ip_network == ine)
    for row in query:
        result.add(row.ip_address)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result
