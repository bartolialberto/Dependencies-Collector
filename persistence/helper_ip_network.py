import ipaddress
from typing import Set
from peewee import DoesNotExist
from persistence.BaseModel import IpNetworkEntity, IpAddressDependsAssociation


def insert(network: str or ipaddress.IPv4Network) -> IpNetworkEntity:
    ip_network = None
    if isinstance(network, str):
        ip_network = ipaddress.IPv4Network(network)
    else:
        ip_network = network
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


def get_all() -> Set[IpNetworkEntity]:
    result = set()
    query = IpNetworkEntity.select()
    for row in query:
        result.add(row)
    return result


def get_of(iae: ipaddress.IPv4Address) -> IpNetworkEntity:
    query = IpAddressDependsAssociation.select()\
        .join_from(IpAddressDependsAssociation, IpNetworkEntity)\
        .where(IpAddressDependsAssociation.ip_address == iae)\
        .limit(1)
    for row in query:
        return row.ip_network
    raise DoesNotExist
