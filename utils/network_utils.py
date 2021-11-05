import socket
import urllib.request


def get_local_ip():
    return socket.gethostbyname(socket.gethostname())


def get_public_ip_from_ident_me():
    return urllib.request.urlopen('https://ident.me').read().decode('utf8')
