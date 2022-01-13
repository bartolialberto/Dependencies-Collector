import ipaddress
from entities.resolvers.IpAsDatabase import EntryIpAsDatabase


class AutonomousSystemResolutionValues:
    def __init__(self):
        self.ip_address = None or ipaddress.IPv4Address
        self.entry = None or EntryIpAsDatabase
        self.belonging_network = None or ipaddress.IPv4Network


class AutonomousSystemResolutionResults:
    def __init__(self):
        self.results = dict()

    def add_name_server(self, name_server: str):
        try:
            self.results[name_server]
        except KeyError:
            self.results[name_server] = AutonomousSystemResolutionValues()

    def set_name_server_to_none(self, for_name_server: str):
        self.results[for_name_server] = None

    def insert_ip_address(self, for_name_server: str, ip_address: ipaddress.IPv4Address):
        self.results[for_name_server].ip_address = ip_address

    def insert_ip_as_entry(self, for_name_server: str, entry: EntryIpAsDatabase or None):
        self.results[for_name_server].entry = entry

    def insert_belonging_network(self, for_name_server: str, network: ipaddress.IPv4Network or None):
        self.results[for_name_server].belonging_network = network

    def merge(self, other: 'AutonomousSystemResolutionResults'):
        for name_server in other.results.keys():
            self.results[name_server] = other.results[name_server]
