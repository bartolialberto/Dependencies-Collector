import ipaddress

from entities.DomainName import DomainName
from entities.resolvers.IpAsDatabase import EntryIpAsDatabase


class AutonomousSystemResolutionResults:
    """
    This class represents the result from the IpAsDatabase resolving after an IP address input.
    In short words consists in more dictionaries that categorizes the server based on the result of the IP-AS database
    resolving.

    1- complete_results: a dictionary that saves IP address as keys and then all the resolved information as tuple with
    length of 4: server name, server type, entry of the IP-AS database and the IP range tsv resolved.

    2- no_ip_range_tsv_results: a dictionary that saves IP address as keys and then all the resolved information as
    tuple with length of 3: server name, server type and the entry of the IP-AS database resolved.

    3- no_as_results: a dictionary that saves IP address as keys and then only the server as tuple with length 2:
    server name and server type resolved.

    4- unresolved_servers: a dictionary that saves the servers name that didn't even resolved the IP address. The server
    name is the key and the value is the server type.

    ...

    Attributes
    ----------
    complete_results : Dict[str, Tuple[str, EntryIpAsDatabase, ipaddress.IPv4Network]]
        The dictionary that contains all the completely resolved servers.
    no_ip_range_tsv_results : Dict[str, Tuple[str, EntryIpAsDatabase]]
        The dictionary that contains all the almost completely resolved servers (no IP range TSV).
    no_as_results : Dict[str, str]
        The dictionary that contains all not-resolved servers.
    unresolved_servers : Set[str]
        The dictionary that contains all the servers that doesn't have an IP address.
    """
    def __init__(self):
        """
        Instantiate the object.

        """
        self.complete_results = dict()
        self.no_ip_range_tsv_results = dict()
        self.no_as_results = dict()
        self.unresolved_servers = set()

    def add_complete_result(self, ip_address: ipaddress.IPv4Address, server: DomainName, entry: EntryIpAsDatabase, ip_range_tsv: ipaddress.IPv4Network) -> None:
        """
        This method adds a complete result.

        :param ip_address: An IP address.
        :type ip_address: ipaddress.IPv4Address
        :param server: A server name.
        :type server: str
        :param entry: An entry of the .tsv database.
        :type entry: EntryIpAsDatabase
        :param ip_range_tsv:
        :type ip_range_tsv: ipaddress.IPv4Network
        """
        try:
            self.complete_results[ip_address.exploded] = (server, entry, ip_range_tsv)
        except KeyError:
            self.complete_results[ip_address.exploded] = (server, entry, ip_range_tsv)

    def add_no_ip_range_tsv_result(self, ip_address: ipaddress.IPv4Address, server: DomainName, entry: EntryIpAsDatabase) -> None:
        """
        This method adds an almost complete result that lacks the IP .tsv range resolution.

        :param ip_address: An IP address.
        :type ip_address: ipaddress.IPv4Address
        :param server: A server name.
        :type server: str
        :param entry: An entry of the .tsv database.
        :type entry: EntryIpAsDatabase
        """
        try:
            self.no_ip_range_tsv_results[ip_address.exploded] = (server, entry)
        except KeyError:
            self.no_ip_range_tsv_results[ip_address.exploded] = (server, entry)

    def add_no_as_result(self, ip_address: ipaddress.IPv4Address, server: DomainName) -> None:
        """
        This method adds an unresolved (in the .tsv database) result.

        :param ip_address: An IP address.
        :type ip_address: ipaddress.IPv4Address
        :param server: A server name.
        :type server: str
        """
        try:
            self.no_as_results[ip_address.exploded] = server
        except KeyError:
            self.no_as_results[ip_address.exploded] = server

    def add_unresolved_server(self, server: DomainName) -> None:
        """
        This method adds an unresolved result (no IP address).

        :param server: A server name.
        :type server: str
        """
        self.unresolved_servers.add(server)

    def merge(self, other: 'AutonomousSystemResolutionResults'):        # FORWARD DECLARATIONS (REFERENCES)
        """
        This method merges another AutonomousSystemResolutionResults object into the self object, precisely merges all
        the inner dictionaries of the two.

        :param other: Another AutonomousSystemResolutionResults object.
        :type other: AutonomousSystemResolutionResults
        """
        for ip_address in other.complete_results.keys():
            ip = ipaddress.IPv4Address(ip_address)
            self.add_complete_result(ip,
                 other.complete_results[ip_address][0],
                 other.complete_results[ip_address][1],
                 other.complete_results[ip_address][2])
        for ip_address in other.no_ip_range_tsv_results.keys():
            ip = ipaddress.IPv4Address(ip_address)
            self.add_no_ip_range_tsv_result(ip,
                other.no_ip_range_tsv_results[ip_address][0],
                other.no_ip_range_tsv_results[ip_address][1])
        for ip_address in other.no_as_results.keys():
            ip = ipaddress.IPv4Address(ip_address)
            self.add_no_as_result(ip, other.no_as_results[ip_address][0])
        for server in other.unresolved_servers:
            self.unresolved_servers.add(server)

