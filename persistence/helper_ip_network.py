import ipaddress
from persistence.BaseModel import IpNetworkEntity, EntryIpAsDatabaseEntity, BelongingNetworkAssociation


def insert_or_get(network: ipaddress.IPv4Network) -> IpNetworkEntity:
    n, created = IpNetworkEntity.get_or_create(compressed_notation=network.compressed)
    return n
