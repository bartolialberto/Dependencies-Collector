import ipaddress
from typing import Set, Tuple
from peewee import DoesNotExist
from persistence import helper_ip_network
from persistence.BaseModel import PrefixesTableAssociation, ROVEntity, AutonomousSystemEntity, \
    IpRangeROVEntity


def insert(irre: IpRangeROVEntity or None, re: ROVEntity or None, ase: AutonomousSystemEntity) -> PrefixesTableAssociation:
    pta, created = PrefixesTableAssociation.get_or_create(ip_range_rov=irre, rov=re, autonomous_system=ase)
    return pta


# TODO: da rifare tutte le query
def get_all_of(ip_network_parameter: IpRangeROVEntity or ipaddress.IPv4Network or str) -> Set[PrefixesTableAssociation]:
    ine = None
    if isinstance(ip_network_parameter, IpRangeROVEntity):
        ine = ip_network_parameter
    elif isinstance(ip_network_parameter, ipaddress.IPv4Network):
        try:
            ine = helper_ip_network.get(ip_network_parameter.compressed)
        except DoesNotExist:
            raise
    else:
        try:
            ine = helper_ip_network.get(ip_network_parameter)
        except DoesNotExist:
            raise
    result = set()
    query = PrefixesTableAssociation.select()\
        .where(PrefixesTableAssociation.ip_network == ine)
    for row in query:
        result.add(row)
    return result


def get_all_from(ase: AutonomousSystemEntity) -> Set[Tuple[IpRangeROVEntity, ROVEntity]]:
    query = PrefixesTableAssociation.select()\
        .join_from(PrefixesTableAssociation, ROVEntity)\
        .join_from(PrefixesTableAssociation, IpRangeROVEntity)\
        .where(PrefixesTableAssociation.autonomous_system == ase)
    result = set()
    for row in query:
        result.add((row.ip_network, row.rov))
    return result
