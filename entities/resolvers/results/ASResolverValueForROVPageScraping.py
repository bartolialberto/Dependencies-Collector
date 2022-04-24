import ipaddress
from entities.EntryIpAsDatabase import EntryIpAsDatabase
from entities.RowPrefixesTable import RowPrefixesTable


class ASResolverValueForROVPageScraping:
    """
    This class represents a collection of infos associated to a name server.
    It main purpose is to serve as 'wrapper'.

    ...

     Attributes
     ----------
     server : str
        A server.
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