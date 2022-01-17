import ipaddress
from entities.resolvers.IpAsDatabase import EntryIpAsDatabase
from entities.resolvers.results.AutonomousSystemResolutionResults import AutonomousSystemResolutionResults, \
    AutonomousSystemResolutionValues
from entities.scrapers.ROVPageScraper import RowPrefixesTable


class ASResolverValueForROVPageScraping:
    """
    This class represents a collection of infos associated to a name server.
    It main purpose is to serve as 'wrapper'.

    ...

     Attributes
     ----------
     name_server : str or None
        A name server.
     entry_as_database : EntryIpAsDatabase or None
        An entry of the IpAsDatabase.
     entry_rov_page : RowPrefixesTable or None
        A row of the prefixes table of the ROVPageScraper or None.
     ip_range_rtsv : ipaddress.IPv4Network or None
        An IP network or None.
    """
    def __init__(self, name_server: str or None, entry_as_database: EntryIpAsDatabase or None, network: ipaddress.IPv4Network or None):
        """
        Initialize the object but sets the 'entry_rov_page' to None, because the idea is that ROVPageScraping it has yet
        to happen, so the object should updated later.

        :param name_server: A name server.
        :type name_server: str
        :param entry_as_database: An entry of the IpAsDatabase.
        :type entry_as_database: EntryIpAsDatabase
        :param network: An IP network or None.
        :type network: ipaddress.IPv4Network or None
        """
        self.name_server = name_server
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

    @staticmethod
    def construct_from(value: AutonomousSystemResolutionValues) -> 'ASResolverValueForROVPageScraping':     # FORWARD DECLARATIONS (REFERENCES)
        """
        This static methods constructs an ASResolverValueForROVPageScraping object from an
        AutonomousSystemResolutionValues object.

        :param value: An AutonomousSystemResolutionValues object.
        :type value: AutonomousSystemResolutionValues
        :return: An ASResolverValueForROVPageScraping object.
        :rtype: ASResolverValueForROVPageScraping
        """
        return ASResolverValueForROVPageScraping(value.name_server, value.entry, value.belonging_network)


class ASResolverResultForROVPageScraping:
    """
    This class represents a reformatted AutonomousSystemResolutionResults object. This reformat consists in reverting
    the dictionary belonging to the AutonomousSystemResolutionResults object in a manner that uses the autonomous
    system's number as keys, then the associated value to such key is another dictionary that uses IP addresses as keys;
    the latter dictionary then associate such keys to a collection of infos, that are all 'contained' in a
    ASResolverValueForROVPageScraping object.

    ...

    Attributes
    ----------
    results : Dict[str, AutonomousSystemResolutionValues]
        The reformatted dictionary.

    """
    def __init__(self, as_results: AutonomousSystemResolutionResults):
        """
        Initialize the object reformatting a AutonomousSystemResolutionResults object.

        :param as_results: An AutonomousSystemResolutionResults object.
        :type as_results: AutonomousSystemResolutionResults
        """
        self.results = dict()
        for ip_address in as_results.results.keys():
            if as_results.results[ip_address].entry.as_number is None:
                continue
            try:
                self.results[as_results.results[ip_address].entry.as_number]
                try:
                    self.results[as_results.results[ip_address].entry.as_number][ip_address]
                except KeyError:
                    self.results[as_results.results[ip_address].entry.as_number][ip_address] = ASResolverValueForROVPageScraping.construct_from(as_results.results[ip_address])
            except KeyError:
                self.results[as_results.results[ip_address].entry.as_number] = dict()
                self.results[as_results.results[ip_address].entry.as_number][ip_address] = ASResolverValueForROVPageScraping.construct_from(as_results.results[ip_address])

