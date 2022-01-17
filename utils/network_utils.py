import ipaddress
import socket


def get_local_ip() -> str:
    """
    Return the local ip address.

    :return: The ip address.
    :rtype: str
    """
    return socket.gethostbyname(socket.gethostname())


def is_ip_address(string: str) -> bool:
    """
    Control if a string is a valid ip address.

    :param string: A string.
    :type string: str
    :return: True or False.
    :rtype: bool
    """
    try:
        ipaddress.ip_address(string)
        return True
    except ValueError:
        return False


def is_in_ip_range(ip: ipaddress.IPv4Address, start_ip_range: ipaddress.IPv4Address, end_ip_range: ipaddress.IPv4Address) -> bool:
    """
    Given a range of ip address, it controls if another ip address is contained in such range.
    Remember this is not commutative: if an address is contained between address A (start_ip_range) and address B
    (end_ip_range), it is not contained between address B (end_ip_range) and address A (start_ip_range).

    :param ip: Ip address to query in the range.
    :type ip: ipaddress.IPv4Address
    :param start_ip_range: Start of the range.
    :type start_ip_range: ipaddress.IPv4Address
    :param end_ip_range: End of the range.
    :type end_ip_range: ipaddress.IPv4Address
    :return: True or False.
    :rtype: bool
    """
    if start_ip_range <= ip <= end_ip_range:
        return True
    else:
        return False


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
    notation) taking 24 bits as mask length.

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
