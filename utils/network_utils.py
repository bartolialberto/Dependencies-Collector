import ipaddress
import socket


def get_local_ip() -> str:
    """
    Return the local ip address as string.

    :return: The ip address.
    :rtype: str
    """
    return socket.gethostbyname(socket.gethostname())


def is_in_network(ip: ipaddress.IPv4Address, network: ipaddress.IPv4Network) -> bool:
    """
    Given a network, it controls if a certain ip address is contained in such network.

    :param ip: Ip address to query in the range.
    :type ip: ipaddress.IPv4Address
    :param network: A network.
    :type network: ipaddress.IPv4Network
    :return: True or False.
    :rtype: bool
    """
    if ip in network:
        return True
    else:
        return False


def get_predefined_network(ip_parameter: ipaddress.IPv4Address or str) -> ipaddress.IPv4Network:
    """
    Given an IP address returns the associated network that changes the last number to zero and then (using compressed
    notation) takes 24 bits as mask length.

    :param ip_parameter: An IP address.
    :type ip_parameter: ipaddress.IPv4Address or str
    :return: The predefined network.
    :rtype: ipaddress.IPv4Network
    """
    if isinstance(ip_parameter, ipaddress.IPv4Address):
        ip = ip_parameter.exploded
    else:
        ip = ip_parameter
    split = ip.split('.')
    return ipaddress.IPv4Network(split[0]+'.'+split[1]+'.'+split[2]+'.0/24')
