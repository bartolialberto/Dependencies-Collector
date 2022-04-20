import ipaddress
from typing import Set
from peewee import DoesNotExist
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence.BaseModel import IpRangeROVEntity, IpAddressDependsAssociation, IpAddressEntity


def insert(network: ipaddress.IPv4Network) -> IpRangeROVEntity:
    irre, created = IpRangeROVEntity.get_or_create(compressed_notation=network.compressed)
    return irre


def get(ip_range_rov: str) -> IpRangeROVEntity:
    try:
        ip = ipaddress.IPv4Network(ip_range_rov)
    except ValueError:
        raise
    try:
        return IpRangeROVEntity.get_by_id(ip.compressed)
    except DoesNotExist:
        raise


def get_of(iae: IpAddressEntity) -> IpRangeROVEntity:
    try:
        iada = IpAddressDependsAssociation.get(IpAddressDependsAssociation.ip_address == iae)
        return iada.ip_range_rov
    except DoesNotExist:
        raise


def get_all_addresses_of(irre: IpRangeROVEntity) -> Set[IpAddressEntity]:
    query = IpAddressDependsAssociation.select()\
        .where(IpAddressDependsAssociation.ip_range_rov == irre)
    result = set()
    for row in query:
        result.add(row.ip_address)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result
