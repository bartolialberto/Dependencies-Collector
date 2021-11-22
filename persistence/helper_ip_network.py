import ipaddress
from persistence.BaseModel import IpNetworkEntity, EntryIpAsDatabaseEntity, BelongingNetworkAssociation


def insert(network: ipaddress.IPv4Network) -> IpNetworkEntity:
    n = IpNetworkEntity.create(compressed_notation=network.compressed)
    return n
