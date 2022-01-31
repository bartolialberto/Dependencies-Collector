import ipaddress
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
        ip = ipaddress.IPv4Address(ip_address)
    except ValueError:
        raise
    try:
        iae = helper_ip_address.get(ip.exploded)
    except DoesNotExist:
        raise
    return get_from_entity_ip_address(iae)


def get_from_entity_ip_address(iae: IpAddressEntity) -> IpAddressDependsAssociation:
    try:
        return IpAddressDependsAssociation.get(IpAddressDependsAssociation.ip_address == iae)
    except DoesNotExist:
        raise


def get_unresolved() -> Set[IpAddressDependsAssociation]:
    query = IpAddressDependsAssociation.select()\
        .where((IpAddressDependsAssociation.ip_range_tsv.is_null(True)) | (IpAddressDependsAssociation.ip_range_rov.is_null(True)))
    result = set()
    for row in query:
        result.add(row)
    return result


def update_ip_network(iada: IpAddressDependsAssociation, new_ine: IpNetworkEntity):
    query = IpAddressDependsAssociation.update(ip_network=new_ine)\
        .where((IpAddressDependsAssociation.ip_address == iada.ip_address) &
               (IpAddressDependsAssociation.ip_range_tsv == iada.ip_range_tsv) &
               (IpAddressDependsAssociation.ip_range_rov == iada.ip_range_rov) &
               (IpAddressDependsAssociation.ip_network == iada.ip_network))
    query.execute()


def update_ip_range_tsv(iada: IpAddressDependsAssociation, new_irte: IpRangeTSVEntity or None):
    query = IpAddressDependsAssociation.update(ip_range_tsv=new_irte)\
        .where((IpAddressDependsAssociation.ip_address == iada.ip_address) &
               (IpAddressDependsAssociation.ip_range_tsv == iada.ip_range_tsv) &
               (IpAddressDependsAssociation.ip_range_rov == iada.ip_range_rov) &
               (IpAddressDependsAssociation.ip_network == iada.ip_network))
    query.execute()


def update_ip_range_rov(iada: IpAddressDependsAssociation, new_irre: IpRangeROVEntity or None):
    query = IpAddressDependsAssociation.update(ip_range_rov=new_irre) \
        .where((IpAddressDependsAssociation.ip_address == iada.ip_address) &
               (IpAddressDependsAssociation.ip_range_tsv == iada.ip_range_tsv) &
               (IpAddressDependsAssociation.ip_range_rov == iada.ip_range_rov) &
               (IpAddressDependsAssociation.ip_network == iada.ip_network))
    query.execute()
