import ipaddress
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


class AutonomousSystemResolutionResults:
    """
    This class represents the result from the IpAsDatabase resolving after an IP address input.
    In short words consists in a dictionary that uses IP addresses as keys and a collection of info related with it as
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

    def add_ip_address(self, ip_address_parameter: str or ipaddress.IPv4Address):
        """
        This method adds (initialize) a new key to the dictionary.

        :param ip_address_parameter: An IP address.
        :type ip_address_parameter: str or ipaddress.IPv4Address
        """
        ip_address_exploded = None
        if isinstance(ip_address_parameter, ipaddress.IPv4Address):
            ip_address_exploded = ip_address_parameter.exploded
        else:
            ip_address_exploded = ip_address_parameter
        try:
            self.results[ip_address_exploded]
        except KeyError:
            self.results[ip_address_exploded] = AutonomousSystemResolutionValues()

    def set_ip_address_to_none(self, for_ip_address_parameter: str or ipaddress.IPv4Address):
        """
        This method sets the value of the IP address key to None.

        :param for_ip_address_parameter: An IP address.
        :type for_ip_address_parameter: str or ipaddress.IPv4Address
        """
        for_ip_address_exploded = None
        if isinstance(for_ip_address_parameter, ipaddress.IPv4Address):
            for_ip_address_exploded = for_ip_address_parameter.exploded
        else:
            for_ip_address_exploded = for_ip_address_parameter
        self.results[for_ip_address_exploded] = None

    def insert_name_server(self, for_ip_address_parameter: str or ipaddress.IPv4Address, name_server: str or None):
        """
        This method sets the name server attribute of the value associated to the IP address key parameter.

        :param for_ip_address_parameter: An IP address.
        :type for_ip_address_parameter: str or ipaddress.IPv4Address
        :param name_server: A name server.
        :type name_server: str or None
        """
        for_ip_address_exploded = None
        if isinstance(for_ip_address_parameter, ipaddress.IPv4Address):
            for_ip_address_exploded = for_ip_address_parameter.exploded
        else:
            for_ip_address_exploded = for_ip_address_parameter
        self.results[for_ip_address_exploded].name_server = name_server

    def insert_ip_as_entry(self, for_ip_address_parameter: str or ipaddress.IPv4Address, entry: EntryIpAsDatabase or None):
        """
        This method sets the entry attribute of the value associated to the IP address key parameter.

        :param for_ip_address_parameter: An IP address.
        :type for_ip_address_parameter: str or ipaddress.IPv4Address
        :param entry: A valid entry or None.
        :type entry: EntryIpAsDatabase or None
        """
        for_ip_address_exploded = None
        if isinstance(for_ip_address_parameter, ipaddress.IPv4Address):
            for_ip_address_exploded = for_ip_address_parameter.exploded
        else:
            for_ip_address_exploded = for_ip_address_parameter
        self.results[for_ip_address_exploded].entry = entry

    def insert_ip_range_tsv(self, for_ip_address_parameter: str or ipaddress.IPv4Address, network: ipaddress.IPv4Network or None):
        """
        This method sets the network attribute of the value associated to the IP address key parameter.

        :param for_ip_address_parameter: An IP address.
        :type for_ip_address_parameter: str or ipaddress.IPv4Address
        :param network: A IP network or None.
        :type network: ipaddress.IPv4Network or None
        """
        for_ip_address_exploded = None
        if isinstance(for_ip_address_parameter, ipaddress.IPv4Address):
            for_ip_address_exploded = for_ip_address_parameter.exploded
        else:
            for_ip_address_exploded = for_ip_address_parameter
        self.results[for_ip_address_exploded].ip_range_tsv = network

    def merge(self, other: 'AutonomousSystemResolutionResults'):        # FORWARD DECLARATIONS (REFERENCES)
        """
        This method merges another AutonomousSystemResolutionResults object into the self object, precisely merges the
        dictionaries of the two.

        :param other: Another AutonomousSystemResolutionResults object.
        :type other: AutonomousSystemResolutionResults
        """
        for ip_address in other.results.keys():
            self.results[ip_address] = other.results[ip_address]
