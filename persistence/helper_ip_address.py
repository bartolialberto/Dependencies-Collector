import ipaddress
from peewee import DoesNotExist
from persistence import helper_access
from persistence.BaseModel import IpAddressEntity, DomainNameEntity


def insert(address_param: str or ipaddress.IPv4Address) -> IpAddressEntity:
    address = None
    if isinstance(address_param, ipaddress.IPv4Address):
        address = address_param
    else:
        try:
            address = ipaddress.IPv4Address(address_param)
        except ValueError:
            raise
    iae, created = IpAddressEntity.get_or_create(exploded_notation=address.exploded)
    return iae


def get(ip_string_exploded_notation: str) -> IpAddressEntity:
    try:
        iae = IpAddressEntity.get_by_id(ip_string_exploded_notation)
    except DoesNotExist:
        raise
    return iae


def get_first_of(dne: DomainNameEntity) -> IpAddressEntity:
    try:
        aa = helper_access.get_first_of(dne)
    except DoesNotExist:
        raise
    try:
        # print(f"DEBUG: aa.ip_address = {aa.ip_address}")
        iae = get(aa.ip_address)
    except DoesNotExist:
        raise
    return iae
