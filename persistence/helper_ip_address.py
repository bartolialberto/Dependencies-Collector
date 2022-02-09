import ipaddress
from typing import Set, List
from peewee import DoesNotExist

from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_domain_name
from persistence.BaseModel import IpAddressEntity, DomainNameEntity, AccessAssociation, IpNetworkEntity, \
    IpAddressDependsAssociation, AliasAssociation


def insert(address_param: str or ipaddress.IPv4Address) -> IpAddressEntity:
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


def get(ip_address: str) -> IpAddressEntity:
    try:
        ip = ipaddress.IPv4Address(ip_address)
    except ValueError:
        raise
    try:
        iae = IpAddressEntity.get_by_id(ip.exploded)
    except DoesNotExist:
        raise
    return iae


def resolve_reversed_access_path(iae: IpAddressEntity, add_dne_along_the_chain: bool) -> Set[DomainNameEntity]:
    query = AccessAssociation.select()\
        .where(AccessAssociation.ip_address == iae)
    result = set()
    canonical_dnes = set()
    for row in query:
        canonical_dnes.add(row.domain_name)
    if len(canonical_dnes) == 0:
        raise NoAvailablePathError(iae.exploded_notation)
    for dne in canonical_dnes:
        chain_dnes = __inner_resolve_reversed_access_path(dne, None)
        if add_dne_along_the_chain:
            for chain_dne in chain_dnes:
                result.add(chain_dne)
        else:
            qname_dne = chain_dnes[-1]
            result.add(qname_dne)
    return result


def __inner_resolve_reversed_access_path(alias_dne: Set[DomainNameEntity], chain_dnes: List[DomainNameEntity] or None) -> List[DomainNameEntity]:
    if chain_dnes is None:
        chain_dnes = list()
    else:
        pass
    chain_dnes.append(alias_dne)
    try:
        aa = AliasAssociation.get(AliasAssociation.alias == alias_dne)
        name_dne = aa.name
    except DoesNotExist:
        return chain_dnes
    return __inner_resolve_reversed_access_path(name_dne, chain_dnes)



def get_first_of(domain_name_parameter: DomainNameEntity or str) -> IpAddressEntity:
    dne = None
    if isinstance(domain_name_parameter, DomainNameEntity):
        dne = domain_name_parameter
    else:
        try:
            dne = helper_domain_name.get(domain_name_parameter)
        except DoesNotExist:
            raise
    query = AccessAssociation.select()\
        .where((AccessAssociation.domain_name == dne) & (AccessAssociation.ip_address.is_null(False)))\
        .limit(1)
    for row in query:
        return row.ip_address
    raise DoesNotExist


def get_all_of(dne: DomainNameEntity) -> Set[IpAddressEntity]:
    result = set()
    query = AccessAssociation.select()\
        .where((AccessAssociation.domain_name == dne) & (AccessAssociation.ip_address.is_null(False)))
    for row in query:
        result.add(row.ip_address)
    return result


def get_all_of_entity_network(ine: IpNetworkEntity) -> Set[IpAddressEntity]:
    result = set()
    query = IpAddressDependsAssociation.select()\
        .where(IpAddressDependsAssociation.ip_network == ine)
    for row in query:
        result.add(row.ip_address)
    return result
