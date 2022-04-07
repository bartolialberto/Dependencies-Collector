import ipaddress
from typing import Set, Union
from peewee import DoesNotExist
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_domain_name, helper_ip_address
from persistence.BaseModel import IpNetworkEntity, IpAddressDependsAssociation, IpAddressEntity, DomainNameEntity
from utils import network_utils


def insert(network_parameter: str or ipaddress.IPv4Network) -> IpNetworkEntity:
    ip_network = None
    if isinstance(network_parameter, str):
        ip_network = ipaddress.IPv4Network(network_parameter)
    else:
        ip_network = network_parameter
    ine, created = IpNetworkEntity.get_or_create(compressed_notation=ip_network.compressed)
    return ine


def insert_from_address_entity(iae: IpAddressEntity) -> IpNetworkEntity:
    ip_network = network_utils.get_predefined_network(iae.exploded_notation)
    ine, created = IpNetworkEntity.get_or_create(compressed_notation=ip_network.compressed)
    return ine


def get(ip_network: ipaddress.IPv4Network) -> IpNetworkEntity:
    try:
        ine = IpNetworkEntity.get_by_id(ip_network.compressed)
    except DoesNotExist:
        raise
    return ine


def get_everyone() -> Set[IpNetworkEntity]:
    result = set()
    query = IpNetworkEntity.select()
    for row in query:
        result.add(row)
    return result


def get_of(iae: IpAddressEntity) -> IpNetworkEntity:
    # TODO: testare... Ha l'attributo ip_network??
    try:
        iada = IpAddressDependsAssociation.get(IpAddressDependsAssociation.ip_address == iae)
        return iada.ip_network
    except DoesNotExist:
        raise


def get_all_addresses_of(ine: IpNetworkEntity) -> Set[IpNetworkEntity]:
    query = IpAddressDependsAssociation.select()\
        .where(IpAddressDependsAssociation.ip_network == ine)
    result = set()
    for row in query:
        result.add(row.ip_address)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result


def get_of_entity_domain_name(dne: DomainNameEntity) -> Set[IpNetworkEntity]:
    try:
        iaes, dnes = helper_domain_name.resolve_a_path(dne, get_only_first_address=False)
    except (NoAvailablePathError, DoesNotExist):
        raise
    result = set()
    for iae in iaes:
        try:
            ine = get_of(iae)
        except DoesNotExist:
            raise
        result.add(ine)
    return result
