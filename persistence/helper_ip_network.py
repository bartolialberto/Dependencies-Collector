import ipaddress
from typing import Set
from peewee import DoesNotExist
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence.BaseModel import IpNetworkEntity, IpAddressDependsAssociation, IpAddressEntity
from utils import network_utils


def insert(ip_network: ipaddress.IPv4Network) -> IpNetworkEntity:
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
    try:
        iada = IpAddressDependsAssociation.get(IpAddressDependsAssociation.ip_address == iae)
        return iada.ip_network
    except DoesNotExist:
        raise


def get_all_addresses_of(ine: IpNetworkEntity) -> Set[IpAddressEntity]:
    query = IpAddressDependsAssociation.select()\
        .where(IpAddressDependsAssociation.ip_network == ine)
    result = set()
    for row in query:
        result.add(row.ip_address)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result
