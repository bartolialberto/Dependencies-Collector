import ipaddress
from persistence.BaseModel import IpNetworkEntity


def insert(network: str or ipaddress.IPv4Network) -> IpNetworkEntity:
    ip_network = None
    if isinstance(network, str):
        ip_network = ipaddress.IPv4Network(network)
    else:
        ip_network = network
    ine, created = IpNetworkEntity.get_or_create(compressed_notation=ip_network.compressed)
    return ine
