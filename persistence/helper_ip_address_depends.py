from typing import Set, List, Dict, Union
from peewee import DoesNotExist
from persistence.BaseModel import IpAddressDependsAssociation, IpAddressEntity, IpNetworkEntity, IpRangeTSVEntity, \
    IpRangeROVEntity


def insert(iae: IpAddressEntity, ine: IpNetworkEntity, irte: IpRangeTSVEntity or None, irre: IpRangeROVEntity or None) -> IpAddressDependsAssociation:
    iada, created = IpAddressDependsAssociation.get_or_create(ip_address=iae, ip_network=ine, ip_range_tsv=irte, ip_range_rov=irre)
    return iada


def bulk_inserts(data_source: List[Dict[str, Union[IpAddressEntity, IpNetworkEntity, IpRangeTSVEntity, IpRangeROVEntity, None]]]) -> None:
    IpAddressDependsAssociation.insert_many(data_source).on_conflict_replace().execute()


def get_from_entity_ip_address(iae: IpAddressEntity) -> IpAddressDependsAssociation:
    try:
        return IpAddressDependsAssociation.get(IpAddressDependsAssociation.ip_address == iae)
    except DoesNotExist:
        raise


def get_unresolved(execute_rov_scraping=True) -> Set[IpAddressDependsAssociation]:
    if execute_rov_scraping:
        query = IpAddressDependsAssociation.select()\
            .where((IpAddressDependsAssociation.ip_range_tsv.is_null(True)) | (IpAddressDependsAssociation.ip_range_rov.is_null(True)))
    else:
        query = IpAddressDependsAssociation.select()\
            .where(IpAddressDependsAssociation.ip_range_tsv.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
