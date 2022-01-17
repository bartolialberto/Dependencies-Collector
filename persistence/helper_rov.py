import ipaddress
from peewee import DoesNotExist
from persistence import helper_ip_network
from persistence.BaseModel import ROVEntity, IpNetworkEntity, PrefixesTableAssociation


def insert(state_string: str, visibility_int: int) -> ROVEntity:
    re, created = ROVEntity.get_or_create(state=state_string, visibility=visibility_int)
    return re


def get_from_network(ip_network_parameter: IpNetworkEntity or ipaddress.IPv4Network or str) -> ROVEntity:
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
        .join_from(PrefixesTableAssociation, ROVEntity)\
        .where(PrefixesTableAssociation.ip_network == ine)
    for row in query:
        return row.rov
    raise DoesNotExist
