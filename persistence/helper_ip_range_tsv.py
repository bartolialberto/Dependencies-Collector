import ipaddress
from persistence.BaseModel import IpRangeTSVEntity


def insert(compressed_notation: str) -> IpRangeTSVEntity:
    network = ipaddress.IPv4Network(compressed_notation)
    irte, created = IpRangeTSVEntity.get_or_create(compressed_notation=network.compressed)
    return irte
