import ipaddress
from typing import Set
from peewee import DoesNotExist
from exceptions.EmptyResultError import EmptyResultError
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_ip_address
from persistence.BaseModel import IpRangeTSVEntity, IpAddressDependsAssociation, IpAddressEntity


def insert(compressed_notation: str) -> IpRangeTSVEntity:
    network = ipaddress.IPv4Network(compressed_notation)
    irte, created = IpRangeTSVEntity.get_or_create(compressed_notation=network.compressed)
    return irte


def get(network: str) -> IpRangeTSVEntity:
    try:
        ip_network = ipaddress.IPv4Network(network)
    except ValueError:
        raise
    try:
        irte = IpRangeTSVEntity.get_by_id(ip_network.compressed)
    except DoesNotExist:
        raise
    return irte


def get_of(iae: IpAddressEntity) -> IpRangeTSVEntity:
    try:
        iada = IpAddressDependsAssociation.get(IpAddressDependsAssociation.ip_address == iae)
        return iada.ip_range_tsv
    except DoesNotExist:
        raise


def get_all_addresses_of(irte: IpRangeTSVEntity) -> Set[IpAddressEntity]:
    query = IpAddressDependsAssociation.select()\
        .where(IpAddressDependsAssociation.ip_range_tsv == irte)
    result = set()
    for row in query:
        result.add(row.ip_address)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result
