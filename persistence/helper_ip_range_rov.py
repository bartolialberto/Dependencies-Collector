import ipaddress
from typing import List
from peewee import DoesNotExist
from exceptions.EmptyResultError import EmptyResultError
from persistence import helper_ip_address
from persistence.BaseModel import IpRangeROVEntity, IpAddressDependsAssociation, IpAddressEntity


def insert(compressed_notation: str) -> IpRangeROVEntity:
    network = ipaddress.IPv4Network(compressed_notation)
    irre, created = IpRangeROVEntity.get_or_create(compressed_notation=network.compressed)
    return irre


def get(ip_range_rov: str) -> IpRangeROVEntity:
    try:
        return IpRangeROVEntity.get_by_id(ip_range_rov)
    except DoesNotExist:
        raise


def get_all_from(address: str) -> List[IpRangeROVEntity]:
    """ Query probably useful only for tests. """
    try:
        iae = helper_ip_address.get(address)
    except DoesNotExist:
        raise
    query = IpAddressDependsAssociation.select()\
        .join(IpRangeROVEntity)\
        .where(IpAddressDependsAssociation.ip_address == iae)
    result = list()
    for row in query:
        result.append(row.ip_range_rov)
    if len(result) == 0:
        raise EmptyResultError
    else:
        return result
