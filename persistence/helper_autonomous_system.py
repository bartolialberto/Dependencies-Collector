import ipaddress
from typing import Set
from peewee import DoesNotExist
from persistence import helper_ip_network
from persistence.BaseModel import AutonomousSystemEntity, IpNetworkEntity, PrefixesTableAssociation


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


def get_all_of(ip_network_parameter: IpNetworkEntity or ipaddress.IPv4Network or str) -> Set[AutonomousSystemEntity]:
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
    result = set()
    query = PrefixesTableAssociation.select()\
        .join_from(PrefixesTableAssociation, AutonomousSystemEntity)\
        .where(PrefixesTableAssociation.ip_network == ine)
    for row in query:
        result.add(row.autonomous_system)
    return result
