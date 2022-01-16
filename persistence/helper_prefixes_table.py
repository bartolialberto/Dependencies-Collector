import ipaddress
from typing import Set
from peewee import DoesNotExist
from persistence import helper_ip_network
from persistence.BaseModel import PrefixesTableAssociation, IpNetworkEntity, ROVEntity, AutonomousSystemEntity


def insert(ine: IpNetworkEntity, re: ROVEntity or None, ase: AutonomousSystemEntity) -> PrefixesTableAssociation:
    pta, created = PrefixesTableAssociation.get_or_create(ip_network=ine, rov=re, autonomous_system=ase)
    return pta


def get_all_of(ip_network_parameter: IpNetworkEntity or ipaddress.IPv4Network or str) -> Set[PrefixesTableAssociation]:
    ine = None
    if isinstance(ip_network_parameter, IpNetworkEntity):
        ine = ip_network_parameter
    elif isinstance(ip_network_parameter, ipaddress.IPv4Network):
        try:
            ine = helper_ip_network.get_first_of(ip_network_parameter.compressed)
        except DoesNotExist:
            raise
    else:
        try:
            ine = helper_ip_network.get_first_of(ip_network_parameter)
        except DoesNotExist:
            raise
    result = set()
    query = PrefixesTableAssociation.select()\
        .where(PrefixesTableAssociation.ip_network == ine)
    for row in query:
        result.add(row)
    return result
