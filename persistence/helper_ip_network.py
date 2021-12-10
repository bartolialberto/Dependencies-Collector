import ipaddress
from persistence.BaseModel import IpNetworkEntity, BelongingNetworkAssociation, EntryIpAsDatabaseEntity, \
    EntryROVPageEntity, PrefixAssociation


def insert_or_get(network: ipaddress.IPv4Network) -> IpNetworkEntity:
    n, created = IpNetworkEntity.get_or_create(compressed_notation=network.compressed)
    return n


def insert(network: ipaddress.IPv4Network) -> IpNetworkEntity:
    ne, created = IpNetworkEntity.get_or_create(compressed_notation=network.compressed)
    return ne


def insert_with_ip_as_relation_too(network: ipaddress.IPv4Network, entry: EntryIpAsDatabaseEntity) -> (IpNetworkEntity, BelongingNetworkAssociation):
    ne = insert(network)
    bna, created = BelongingNetworkAssociation.get_or_create(entry=entry.id, network=ne.id)
    return ne, bna


def insert_with_rov_page_relation_too(network: ipaddress.IPv4Network, entry: EntryROVPageEntity) -> (IpNetworkEntity, PrefixAssociation):
    ne = insert(network)
    pa, created = PrefixAssociation.get_or_create(entry=entry.id, network=ne.id)
    return ne, pa
