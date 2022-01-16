import ipaddress
from entities.resolvers.IpAsDatabase import EntryIpAsDatabase


class AutonomousSystemResolutionValues:
    """
    This class represents a collection of infos associated to a name server.
    It main purpose is to serve as 'wrapper'.

    ...

     Attributes
     ----------
     ip_address : ipaddress.IPv4Address or None
        An IP address or None.
     entry : EntryIpAsDatabase
        An entry of the IpAsDatabase.
     belonging_network : ipaddress.IPv4Network or None
        An IP network or None.
    """
    def __init__(self):
        self.ip_address = ipaddress.IPv4Address
        self.entry = None or EntryIpAsDatabase
        self.belonging_network = None or ipaddress.IPv4Network


class AutonomousSystemResolutionResults:
    """
    This class represents the result from the IpAsDatabase resolving after an IP address input.
    In short words consists in a dictionary that uses name servers as keys and a collection of info related with it as
    values, those collection of infos is represented by an AutonomousSystemResolutionValues object.

    ...

    Attributes
    ----------
    results : Dict[str, AutonomousSystemResolutionValues]
        The dictionary that associate a name server with an AutonomousSystemResolutionValues object.

    """
    def __init__(self):
        """
        Instantiate the object.

        """
        self.results = dict()

    def add_name_server(self, name_server: str):
        """
        This method adds (initialize) a new key to the dictionary.

        :param name_server: A name server.
        :type name_server: str
        """
        try:
            self.results[name_server]
        except KeyError:
            self.results[name_server] = AutonomousSystemResolutionValues()

    def set_name_server_to_none(self, for_name_server: str):
        """
        This method sets the value of the name server key to None.

        :param for_name_server: A name server.
        :type for_name_server: str
        """
        self.results[for_name_server] = None

    def insert_ip_address(self, for_name_server: str, ip_address: ipaddress.IPv4Address):
        """
        This method sets the ip address attribute of the value associated to the name server key parameter.

        :param for_name_server: A name server.
        :type for_name_server: str
        :param ip_address: An IP address.
        :type ip_address: ipaddress.IPv4Address
        """
        self.results[for_name_server].ip_address = ip_address

    def insert_ip_as_entry(self, for_name_server: str, entry: EntryIpAsDatabase or None):
        """
        This method sets the entry attribute of the value associated to the name server key parameter.

        :param for_name_server: A name server.
        :type for_name_server: str
        :param entry: A valid entry or None.
        :type entry: EntryIpAsDatabase or None
        """
        self.results[for_name_server].entry = entry

    def insert_belonging_network(self, for_name_server: str, network: ipaddress.IPv4Network or None):
        """
        This method sets the network attribute of the value associated to the name server key parameter.

        :param for_name_server: A name server.
        :type for_name_server: str
        :param network: A IP network or None.
        :type network: ipaddress.IPv4Network or None
        """
        self.results[for_name_server].belonging_network = network

    def merge(self, other: 'AutonomousSystemResolutionResults'):        # FORWARD DECLARATIONS (REFERENCES)
        """
        This method merges another AutonomousSystemResolutionResults object into the self object, precisely merges the
        dictionaries of the two.

        :param other: Another AutonomousSystemResolutionResults object.
        :type other: AutonomousSystemResolutionResults
        """
        for name_server in other.results.keys():
            self.results[name_server] = other.results[name_server]
