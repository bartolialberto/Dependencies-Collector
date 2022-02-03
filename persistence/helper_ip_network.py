import ipaddress
from typing import Set
from peewee import DoesNotExist
from persistence import helper_domain_name
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


def get(ip_network_parameter: ipaddress.IPv4Network or str) -> IpNetworkEntity:
    network = None
    if isinstance(ip_network_parameter, ipaddress.IPv4Network):
        network = ip_network_parameter
    else:
        try:
            network = ipaddress.IPv4Network(ip_network_parameter)
        except ValueError:
            raise
    try:
        ine = IpNetworkEntity.get_by_id(network.compressed)
    except DoesNotExist:
        raise
    return ine


def get_everyone() -> Set[IpNetworkEntity]:
    result = set()
    query = IpNetworkEntity.select()
    for row in query:
        result.add(row)
    return result


def get_of(iae: ipaddress.IPv4Address) -> IpNetworkEntity:
    query = IpAddressDependsAssociation.select()\
        .where(IpAddressDependsAssociation.ip_address == iae)\
        .limit(1)
    for row in query:
        return row.ip_network
    raise DoesNotExist


def get_of_entity_domain_name(dne: DomainNameEntity) -> Set[IpNetworkEntity]:
    iaes = helper_domain_name.resolve_access_path(dne, get_only_first_address=False)
    result = set()
    for iae in iaes:
        try:
            ine = get_of(iae)
        except DoesNotExist:
            raise
        result.add(ine)
    return result
