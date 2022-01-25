from typing import List, Tuple
from peewee import DoesNotExist
from exceptions.EmptyResultError import EmptyResultError
from persistence import helper_ip_address
from persistence.BaseModel import ROVEntity, PrefixesTableAssociation, IpAddressDependsAssociation, IpRangeROVEntity


def insert(state_string: str, visibility_int: int) -> ROVEntity:
    re, created = ROVEntity.get_or_create(state=state_string, visibility=visibility_int)
    return re


def get_all_from(address: str, with_ip_range_rov_string: bool) -> List[ROVEntity] or List[Tuple[ROVEntity, str]]:
    """ Query probably useful only for tests. """
    try:
        iae = helper_ip_address.get(address)
    except DoesNotExist:
        raise
    query = ROVEntity.select(ROVEntity, IpRangeROVEntity)\
        .join(PrefixesTableAssociation)\
        .join(IpRangeROVEntity)\
        .join(IpAddressDependsAssociation) \
        .where(IpAddressDependsAssociation.ip_address == iae)
    result = list()
    if with_ip_range_rov_string:
        for row in query.objects():
            result.append((row, row.compressed_notation))
        if len(result) == 0:
            raise EmptyResultError
        else:
            return result
    else:
        for row in query:
            result.append(row)
        if len(result) == 0:
            raise EmptyResultError
        else:
            return result
