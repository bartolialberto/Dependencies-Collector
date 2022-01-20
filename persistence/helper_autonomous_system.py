import ipaddress
from typing import Set, List, Tuple, Dict
from peewee import DoesNotExist
from persistence import helper_ip_network, helper_ip_address, helper_ip_range_tsv, helper_ip_range_rov
from persistence.BaseModel import AutonomousSystemEntity, IpNetworkEntity, PrefixesTableAssociation, IpRangeROVEntity, \
    IpAddressDependsAssociation, IpAddressEntity, IpRangeTSVEntity


def insert(as_number: int) -> AutonomousSystemEntity:
    ase, created = AutonomousSystemEntity.get_or_create(number=as_number)
    return ase


def get_first_of(ip_network_parameter: IpNetworkEntity or ipaddress.IPv4Network or str) -> AutonomousSystemEntity:
    ine = None
    if isinstance(ip_network_parameter, IpNetworkEntity):
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

    query = PrefixesTableAssociation.select()\
        .join_from(PrefixesTableAssociation, AutonomousSystemEntity)\
        .where(PrefixesTableAssociation.ip_network == ine)\
        .limit(1)
    for row in query:
        return row.autonomous_system
    raise DoesNotExist
