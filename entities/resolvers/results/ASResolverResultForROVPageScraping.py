import ipaddress
from entities.enums.ServerTypes import ServerTypes
from entities.resolvers.IpAsDatabase import EntryIpAsDatabase
from entities.resolvers.results.AutonomousSystemResolutionResults import AutonomousSystemResolutionResults
from entities.scrapers.ROVPageScraper import RowPrefixesTable


# TODO: docs
class ASResolverValueForROVPageScraping:
    """
    This class represents a collection of infos associated to a name server.
    It main purpose is to serve as 'wrapper'.

    ...

     Attributes
     ----------
     server : str
        A server.
    server_type : ServerTypes
        The corresponding server type of the server attribute.
     entry_as_database : EntryIpAsDatabase or None
        An entry of the IpAsDatabase.
     entry_rov_page : RowPrefixesTable or None
        A row of the prefixes table of the ROVPageScraper or None.
     ip_range_tsv : ipaddress.IPv4Network or None
        An IP network or None.
    """
    def __init__(self, server: str, entry_as_database: EntryIpAsDatabase, network: ipaddress.IPv4Network or None):
        """
        Initialize the object but sets the 'entry_rov_page' to None, because the idea is that ROVPageScraping it has yet
        to happen, so the object should updated later.

        :param server: A server.
        :type server: str
        :param server_type: The corresponding server type of the server.
        :type server_type: ServerTypes
        :param entry_as_database: An entry of the IpAsDatabase.
        :type entry_as_database: EntryIpAsDatabase
        :param network: An IP network or None.
        :type network: ipaddress.IPv4Network or None
        """
        self.server = server
        self.entry_as_database = entry_as_database
        self.entry_rov_page = None
        self.ip_range_tsv = network

    def insert_rov_entry(self, entry: RowPrefixesTable or None):
        """
        This method updates the 'entry_rov_page' attribute.

        :param entry: A row of the prefixes table of the ROVPageScraper or None.
        :type entry: RowPrefixesTable or None
        """
        self.entry_rov_page = entry

    def __str__(self) -> str:
        """
        This method returns a string representation of this object.

        :return: A string representation of this object.
        :rtype: str
        """
        return f"{self.server},{str(self.entry_as_database)},{str(self.entry_rov_page)},{self.ip_range_tsv.compressed}"


class ASResolverResultForROVPageScraping:
    """
    This class represents a reformatted AutonomousSystemResolutionResults object. This reformat consists 3 different
    dictionaries:

    1- results: this dictionary consists in reverting the dictionary of results that are resolved completely (it means
    that from the IP address we got the server and its type, the entry from the IP-AS database and the IP range tsv even
    if it is not found [None value]) belonging to the AutonomousSystemResolutionResults object in a manner that uses the
    autonomous system's number as keys, then the associated value to such key is another dictionary that uses IP
    addresses as keys; the latter dictionary then associate such keys to a collection of infos, that are all 'contained'
    in a tuple of 4 elements.

    2- no_as_results: this dictionary is used to save the IP addresses that didn't resolved in the IP-AS database. It
    uses IP address as key and for values set a tuple of 2 elements: the server name and its type

    2- unresolved_servers: this dictionary is used to save the servers that didn't resolved even in a IP address. It
    uses server name as key and then the server type as value.

    ...

    Attributes
    ----------
    results : Dict[str, Tuple[str, ServerTypes, EntryIpAsDatabase, ipaddress.IPv4Network]]
        The reformatted dictionary containing the completely resolved results.
    no_as_results : Dict[str, Tuple[str, ServerTypes]]
        The reformatted dictionary containing the results that didn't have a resolution from the IP-AS database.
    unresolved_servers : Dict[str, ServerTypes]
        The reformatted dictionary.
    """
    def __init__(self, as_results: AutonomousSystemResolutionResults):
        """
        Initialize the object reformatting a AutonomousSystemResolutionResults object.

        :param as_results: An AutonomousSystemResolutionResults object.
        :type as_results: AutonomousSystemResolutionResults
        """
        self.results = dict()
        self.no_as_results = dict()
        self.unresolved_servers = set()

        for ip_address in as_results.complete_results.keys():
            server = as_results.complete_results[ip_address][0]
            entry_ip_as_database = as_results.complete_results[ip_address][1]
            ip_range_tsv = as_results.complete_results[ip_address][2]
            try:
                self.results[entry_ip_as_database.as_number]
                try:
                    self.results[entry_ip_as_database.as_number][ip_address]
                except KeyError:
                    self.results[entry_ip_as_database.as_number][ip_address] = ASResolverValueForROVPageScraping(server, entry_ip_as_database, ip_range_tsv)
            except KeyError:
                self.results[entry_ip_as_database.as_number] = dict()
                self.results[entry_ip_as_database.as_number][ip_address] = ASResolverValueForROVPageScraping(server, entry_ip_as_database, ip_range_tsv)

        for ip_address in as_results.no_ip_range_tsv_results.keys():
            server = as_results.no_ip_range_tsv_results[ip_address][0]
            entry_ip_as_database = as_results.no_ip_range_tsv_results[ip_address][1]
            try:
                self.results[entry_ip_as_database.as_number]
                try:
                    self.results[entry_ip_as_database.as_number][ip_address]
                except KeyError:
                    self.results[entry_ip_as_database.as_number][ip_address] = ASResolverValueForROVPageScraping(server, entry_ip_as_database, None)
            except KeyError:
                self.results[entry_ip_as_database.as_number] = dict()
                self.results[entry_ip_as_database.as_number][ip_address] = ASResolverValueForROVPageScraping(server, entry_ip_as_database, None)

        # get IP from name server of a zone but can't resolve that in the .tsv database
        self.no_as_results = as_results.no_as_results

        # get name server from a zone but can't resolve the IP address
        self.unresolved_servers = as_results.unresolved_servers
