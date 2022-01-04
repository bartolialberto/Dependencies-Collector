import ipaddress
from persistence.BaseModel import IpAddressEntity


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
