import ipaddress
from persistence.BaseModel import IpRangeROVEntity


def insert(compressed_notation: str) -> IpRangeROVEntity:
    network = ipaddress.IPv4Network(compressed_notation)
    irre, created = IpRangeROVEntity.get_or_create(compressed_notation=network.compressed)
    return irre
