import ipaddress
from entities.enums.ServerTypes import ServerTypes
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
    complete_results : Dict[str, Tuple[str, ServerTypes, EntryIpAsDatabase, ipaddress.IPv4Network]]
        The dictionary that contains all the completely resolved servers.
    no_ip_range_tsv_results : Dict[str, Tuple[str, ServerTypes, EntryIpAsDatabase]]
        The dictionary that contains all the almost completely resolved servers (no IP range TSV).
    complete_results : Dict[str, Tuple[str, ServerTypes]]
        The dictionary that contains all not-resolved servers.
    complete_results : Dict[str, ServerTypes]
        The dictionary that contains all the servers that doesn't have an IP address.
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
        try:
            self.complete_results[ip_address.exploded]
            old_server = self.complete_results[ip_address.exploded][0]
            old_server_type = self.complete_results[ip_address.exploded][1]
            old_entry_as_database = self.complete_results[ip_address.exploded][2]
            old_ip_range_tsv = self.complete_results[ip_address.exploded][3]
            self.complete_results[ip_address.exploded] = (old_server, ServerTypes.parse_multiple_types(old_server_type, server_type), old_entry_as_database, old_ip_range_tsv)
        except KeyError:
            self.complete_results[ip_address.exploded] = (server, server_type, entry, ip_range_tsv)

    def add_no_ip_range_tsv_result(self, ip_address: ipaddress.IPv4Address, server: str, server_type: ServerTypes, entry: EntryIpAsDatabase) -> None:
        try:
            self.no_ip_range_tsv_results[ip_address.exploded]
            old_server = self.no_ip_range_tsv_results[ip_address.exploded][0]
            old_server_type = self.no_ip_range_tsv_results[ip_address.exploded][1]
            old_entry_as_database = self.no_ip_range_tsv_results[ip_address.exploded][2]
            self.no_ip_range_tsv_results[ip_address.exploded] = (old_server, ServerTypes.parse_multiple_types(old_server_type, server_type), old_entry_as_database)
        except KeyError:
            self.no_ip_range_tsv_results[ip_address.exploded] = (server, server_type, entry)

    def add_no_as_result(self, ip_address: ipaddress.IPv4Address, server: str, server_type: ServerTypes) -> None:
        try:
            self.no_as_results[ip_address.exploded]
            old_server = self.no_as_results[ip_address.exploded][0]
            old_server_type = self.no_as_results[ip_address.exploded][1]
            self.no_as_results[ip_address.exploded] = (old_server, ServerTypes.parse_multiple_types(old_server_type, server_type))
        except KeyError:
            self.no_as_results[ip_address.exploded] = (server, server_type)

    def add_unresolved_server(self, server: str, server_type: ServerTypes) -> None:
        try:
            self.unresolved_servers[server]
            old_server_type = self.unresolved_servers[server]
            self.unresolved_servers[server] = ServerTypes.parse_multiple_types(old_server_type, server_type)
        except KeyError:
            self.unresolved_servers[server] = server_type

    def merge(self, other: 'AutonomousSystemResolutionResults'):        # FORWARD DECLARATIONS (REFERENCES)
        """
        This method merges another AutonomousSystemResolutionResults object into the self object, precisely merges all
        the inner dictionaries of the two.

        :param other: Another AutonomousSystemResolutionResults object.
        :type other: AutonomousSystemResolutionResults
        """
        self.no_ip_range_tsv_results = dict()
        self.no_as_results = dict()
        self.unresolved_servers = dict()
        for ip_address in other.complete_results.keys():
            ip = ipaddress.IPv4Address(ip_address)
            self.add_complete_result(ip,
                 other.complete_results[ip_address][0],
                 other.complete_results[ip_address][1],
                 other.complete_results[ip_address][2],
                 other.complete_results[ip_address][3])
        for ip_address in other.no_ip_range_tsv_results.keys():
            ip = ipaddress.IPv4Address(ip_address)
            self.add_no_ip_range_tsv_result(ip,
                other.no_ip_range_tsv_results[ip_address][0],
                other.no_ip_range_tsv_results[ip_address][1],
                other.no_ip_range_tsv_results[ip_address][2])
        for ip_address in other.no_as_results.keys():
            ip = ipaddress.IPv4Address(ip_address)
            self.add_no_as_result(ip,
                other.no_as_results[ip_address][0],
                other.no_as_results[ip_address][1])
        for server in other.unresolved_servers.keys():
            self.add_unresolved_server(server, other.no_as_results[server])

