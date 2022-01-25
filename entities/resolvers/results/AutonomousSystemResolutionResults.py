import ipaddress

from entities.enums.ServerTypes import ServerTypes
from entities.resolvers.IpAsDatabase import EntryIpAsDatabase


class AutonomousSystemResolutionValues:
    """
    This class represents a collection of infos associated to an IP address.
    It main purpose is to serve as 'wrapper'.

    ...

     Attributes
     ----------
     name_server : str or None
        A name server.
     entry : EntryIpAsDatabase
        An entry of the IpAsDatabase.
     ip_range_tsv : ipaddress.IPv4Network or None
        An IP network or None.
    """
    def __init__(self):
        self.name_server = str or None
        self.entry = None or EntryIpAsDatabase
        self.ip_range_tsv = None or ipaddress.IPv4Network


# TODO: docs
class AutonomousSystemResolutionResults:
    """
    This class represents the result from the IpAsDatabase resolving after an IP address input.
    In short words consists in a dictionary that uses IP addresses as keys and a collection of info related with it as
    values, those collection of infos is represented by an AutonomousSystemResolutionValues object.

    ...

    Attributes
    ----------
    complete_results : Dict[str, AutonomousSystemResolutionValues]
        The dictionary that associate a name server with an AutonomousSystemResolutionValues object.
    """
    def __init__(self):
        """
        Instantiate the object.

        """
        self.complete_results = dict()
        self.no_ip_range_tsv_results = dict()
        self.no_as_results = dict()
        self.unresolved_servers = dict()

    def add_complete_result(self, ip_address: ipaddress.IPv4Address, server: str, server_type: ServerTypes, entry: EntryIpAsDatabase, ip_range_tsv: ipaddress.IPv4Network) -> None:
        self.complete_results[ip_address.exploded] = (server, server_type, entry, ip_range_tsv)

    def add_no_ip_range_tsv_result(self, ip_address: ipaddress.IPv4Address, server: str, server_type: ServerTypes, entry: EntryIpAsDatabase) -> None:
        self.no_ip_range_tsv_results[ip_address.exploded] = (server, server_type, entry)

    def add_no_as_result(self, ip_address: ipaddress.IPv4Address, server: str, server_type: ServerTypes) -> None:
        self.no_as_results[ip_address.exploded] = (server, server_type)

    def add_unresolved_server(self, server: str, server_type: ServerTypes) -> None:
        self.unresolved_servers[server] = server_type

    def merge(self, other: 'AutonomousSystemResolutionResults'):        # FORWARD DECLARATIONS (REFERENCES)
        """
        This method merges another AutonomousSystemResolutionResults object into the self object, precisely merges the
        dictionaries of the two.

        :param other: Another AutonomousSystemResolutionResults object.
        :type other: AutonomousSystemResolutionResults
        """
        self.no_ip_range_tsv_results = dict()
        self.no_as_results = dict()
        self.unresolved_servers = dict()
        for ip_address in other.complete_results.keys():
            self.complete_results[ip_address] = other.complete_results[ip_address]
        for ip_address in other.no_ip_range_tsv_results.keys():
            self.no_ip_range_tsv_results[ip_address] = other.no_ip_range_tsv_results[ip_address]
        for ip_address in other.no_as_results.keys():
            self.no_as_results[ip_address] = other.no_as_results[ip_address]
        for server in other.unresolved_servers.keys():
            self.unresolved_servers[server] = other.unresolved_servers[server]

