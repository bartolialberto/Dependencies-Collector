import ipaddress
import socket
import urllib.request


def get_local_ip():
    return socket.gethostbyname(socket.gethostname())


def get_public_ip_from_ident_me():
    return urllib.request.urlopen('https://ident.me').read().decode('utf8')


def is_ip_address(string: str) -> bool:
    try:
        ipaddress.ip_address(string)
        return True
    except ValueError:
        return False


def is_in_ip_range(ip: ipaddress.IPv4Address, start_ip_range: ipaddress.IPv4Address, end_ip_range: ipaddress.IPv4Address) -> bool:
    if start_ip_range <= ip <= end_ip_range:
        return True
    else:
        return False


def is_in_network(ip: ipaddress.IPv4Address, network: ipaddress.IPv4Network) -> bool:
    if ip in network:
        return True
    else:
        return False
