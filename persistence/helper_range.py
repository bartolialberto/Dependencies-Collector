import ipaddress
from persistence.BaseModel import IpRangeEntity


def insert_or_get(start_ip: ipaddress.IPv4Address, end_ip: ipaddress.IPv4Address) -> IpRangeEntity:
    r, created = IpRangeEntity.get_or_create(start=start_ip.compressed, end=end_ip.compressed)
    return r
