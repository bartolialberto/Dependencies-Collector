import ipaddress
from typing import List
from peewee import DoesNotExist
from exceptions.EmptyResultError import EmptyResultError
from persistence import helper_ip_address
from persistence.BaseModel import IpRangeTSVEntity, IpAddressDependsAssociation


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


def get_all_from(address: str) -> List[IpRangeTSVEntity]:
    """ Query probably useful only for tests. """
    try:
        iae = helper_ip_address.get(address)
    except DoesNotExist:
        raise
    query = IpAddressDependsAssociation.select()\
        .join(IpRangeTSVEntity)\
        .where(IpAddressDependsAssociation.ip_address == iae)
    result = list()
    for row in query:
        result.append(row.ip_range_tsv)
    if len(result) == 0:
        raise EmptyResultError
    else:
        return result
