from typing import Set
from peewee import DoesNotExist
from persistence import helper_ip_address
from persistence.BaseModel import IpAddressDependsAssociation, IpAddressEntity, IpNetworkEntity, IpRangeTSVEntity, \
    IpRangeROVEntity


def insert(iae: IpAddressEntity, ine: IpNetworkEntity or None, irte: IpRangeTSVEntity or None, irre: IpRangeROVEntity or None) -> IpAddressDependsAssociation:
    iada, created = IpAddressDependsAssociation.get_or_create(ip_address=iae, ip_network=ine, ip_range_tsv=irte, ip_range_rov=irre)
    return iada


def get_from_string_ip_address(ip_address: str) -> IpAddressDependsAssociation:
    try:
        iae = helper_ip_address.get(ip_address)
    except DoesNotExist:
        raise
    return get_from_entity_ip_address(iae)


def get_from_entity_ip_address(iae: IpAddressEntity) -> IpAddressDependsAssociation:
    try:
        return IpAddressDependsAssociation.get(IpAddressDependsAssociation.ip_address == iae)
    except DoesNotExist:
        raise


def delete_by_id(entity_id: int):
    try:
        iada = IpAddressDependsAssociation.get_by_id(entity_id)
    except DoesNotExist:
        return
    iada.delete_instance()


def get_unresolved() -> Set[IpAddressDependsAssociation]:
    """
    .join(IpAddressEntity, on=(IpAddressDependsAssociation.ip_address == IpAddressEntity))\
    .join(IpRangeTSVEntity, on=(IpAddressDependsAssociation.ip_range_tsv == IpRangeTSVEntity))\
    .join(IpRangeROVEntity, on=(IpAddressDependsAssociation.ip_range_rov == IpRangeROVEntity))\
    .where((IpAddressDependsAssociation.ip_range_tsv.is_null()) | (IpAddressDependsAssociation.ip_range_rov.is_null()))
    """
    query = IpAddressDependsAssociation.select().where((IpAddressDependsAssociation.ip_range_tsv.is_null(True)) | (IpAddressDependsAssociation.ip_range_rov.is_null(True)))

    result = set()
    for row in query:
        result.add(row)
    return result
