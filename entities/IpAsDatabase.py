import csv
import ipaddress
from pathlib import Path
from typing import List
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import network_utils
from utils import file_utils


class StringEntryIpAsDatabase:
    """
    This class represent the same entity as EntryIpAsDatabase, the only difference is that all attributes are string.
    This is done because the basic idea is:
    1) download the database (see https://iptoasn.com/) and put downloaded file in the input folder
        (in project root folder)
    2) instantiating an IpAsDatabase object will load all entries of the database in the entries attribute automatically
        because the code will navigate the input folder searching the first occurrence of a .tsv file.
        The entries attribute is a list of StringEntryIpAsDatabase and not EntryIpAsDatabase because the database will
        contain around half a million entries, so if we instantiate for every entry (entry == row) an
        EntryIpAsDatabase performance will be worse than instantiating a StringEntryIpAsDatabase. In this manner to
        resolve the ip parameter will require only an instantiation of the first ip address in the entry
        (start_ip_range as ipaddress.Ipv4Address object).
    3) only after the resolution of the ip address to an entry of the database, the entry is instantiated as a
        EntryIpAsDatabase object. Therefore EntryIpAsDatabase is use only for yielding the result of the method that
        is concerned with the resolution.
    The format of an entry as StringEntryIpAsDatabase is exactly described as in https://iptoasn.com/. If we want to
    reiterate that:         range_start     range_end   AS_number   country_code    AS_description
    and every entity is TAB separated

    Attributes
    ----------
    start_ip_range : `str`
        The start of the ip range. Should be an ip address
    end_ip_range : `str`
        The end of the ip range. Should be an ip address
    as_number : `str`
        Should be the Autonomous System number
    country_code : `str`
        Should be the country code
    as_description : `str`
        Should be the Autonomous System brief description
    """
    start_ip_range: str
    end_ip_range: str
    as_number: str
    country_code: str
    as_description: str

    def __init__(self, entries_inline: List[str]):
        """
        Instantiate a StringEntryIpAsDatabase object from a list of string follow format described in
        https://iptoasn.com/; list probably split with a character separator from an entire single string.

        Parameters
        ----------
        entries_inline : `list[str]`
            List of string to associate to each entity of the entry.

        Raises
        ------
        ValueError
            If the number of entities is not correct (5).
        """
        if len(entries_inline) != 5:
            raise ValueError
        else:
            self.start_ip_range = entries_inline[0]
            self.end_ip_range = entries_inline[1]
            self.as_number = entries_inline[2]
            self.country_code = entries_inline[3]
            self.as_description = entries_inline[4]

    def __str__(self):
        return f"{self.start_ip_range}\t{self.end_ip_range}\t{self.as_number}\t{self.country_code}\t{self.as_description}"


class EntryIpAsDatabase:
    """
    This class represent an entry in the database as describe in https://iptoasn.com/ using more convenient object's
    type rather than string. Also, provides some useful methods.

    ...

    Attributes
    ----------
    start_ip_range : `ipaddress.IPv4Address`
        The start of the ip range. It's an ip address.
    end_ip_range : `ipaddress.IPv4Address`
        The end of the ip range. It's an ip address.
    as_number : `int`
        The Autonomous System number. It's a number.
    country_code : `str`
        Should be the country code.
    as_description : `str`
        Should be the Autonomous System brief description.
    """
    start_ip_range: ipaddress.IPv4Address
    end_ip_range: ipaddress.IPv4Address
    as_number: int
    country_code: str
    as_description: str

    def __init__(self, entry: StringEntryIpAsDatabase):
        """
        Instantiate a EntryIpAsDatabase object from a StringEntryIpAsDatabase object to emphasize the fact that an
        EntryIpAsDatabase object is used at the end of the research.

        Parameters
        ----------
        entry : `StringEntryIpAsDatabase`
            Corresponding StringEntryIpAsDatabase object.

        Raises
        ------
        ValueError
            If entry.start_ip_range is not a valid ipaddress.Ipv4Address.
            If entry.end_ip_range is not a valid ipaddress.Ipv4Address.
            If entry.as_number is not a valid integer number.
        """
        try:
            tmp = ipaddress.ip_address(entry.start_ip_range)
            self.start_ip_range = tmp
        except ValueError:
            raise
        try:
            tmp = ipaddress.ip_address(entry.end_ip_range)
            self.end_ip_range = tmp
        except ValueError:
            raise
        try:
            tmp = int(entry.as_number)
            self.as_number = tmp
        except ValueError:
            raise
        self.country_code = entry.country_code
        self.as_description = entry.as_description

    def get_all_networks(self) -> List[ipaddress.IPv4Network]:
        """
        Return a list from the summarized network range given the first and last IP addresses of the range in the
        entry (self object).

        Returns
        ------
        A list of valid ipaddress.IPv4Network.

        Raises
        ------
        TypeError
            If first or last are not IP addresses or are not of the same version.
            If last is not greater than first or if first address version is not 4 or 6
        """
        try:
            return list(ipaddress.summarize_address_range(self.start_ip_range, self.end_ip_range))
        except TypeError:
            raise       # if first or last are not IP addresses or are not of the same version
        except ValueError:
            raise       # if last is not greater than first or if first address version is not 4 or 6

    def get_network_of_ip(self, ip: ipaddress.IPv4Address) -> ipaddress.IPv4Network:
        """
        Return the network from the summarized network range given the first and last IP addresses of the range in the
        entry (self object) and the ip address as parameter.

        Parameters
        ----------
        ip : `ipaddress.IPv4Address`
            Ip address.

        Returns
        -------
        An ipaddress.IPv4Network object.

        Raises
        ------
        ValueError
            If there's not a network in which is contained the ip address parameter.
        """
        networks = self.get_all_networks()
        for network in networks:
            if ip in network:
                return network
        raise ValueError()

    def __str__(self):
        return f"{str(self.start_ip_range)}\t{str(self.end_ip_range)}\t{str(self.as_number)}\t{self.country_code}\t{self.as_description}"


class IpAsDatabase:
    """
    This class represent an object that read the .tsv database inserted in the input folder of the project directory
    and provides the necessary methods to query such database to return a match with an Autonomous System.

    Attributes
    ----------
    filepath : `str`
        If found, it is the absolute filepath of the .tsv database.
    column_separator : `str`
        The character separator between every column-value of each entry
    entries : `list[StringEntryIpAsDatabase]`
        If the database is valid, these are all the entries of the database.
    """
    filepath: str
    column_separator: str
    entries: List[StringEntryIpAsDatabase]

    def __init__(self, column_separator='\t'):      # FileNotFoundError, '\t' = TAB
        """
        Instantiate an IpAsDatabase object setting the filepath of the .tsv database file and then the file is read
        in order to populate a list with all the database entries.

        Parameters
        ----------
        column_separator : `str`, optional
            The character separator between every column-value of each entry

        Raises
        ------
        FileWithExtensionNotFoundError
            If the database .tsv file is not found.
        """
        try:
            result = file_utils.search_for_file_type_in_subdirectory(Path.cwd().parent, "input", ".tsv")
        except FileWithExtensionNotFoundError:
            raise
        file = result[0]
        filepath = str(file)
        try:
            with open(filepath, "r", encoding='utf-8') as f:
                f.close()
            self.filepath = filepath
            self.column_separator = column_separator
            self.entries = list()
            self.load()
        except OSError:
            raise

    def resolve_range(self, ip: ipaddress.IPv4Address) -> EntryIpAsDatabase:
        """
        Method that is concerned to resolve the ip parameter using the database. It use a binary search approach
        considering that the .tsv database is ordered (watch attribute start_ip_range) to gain performance.

        Parameters
        ----------
        ip : `ipaddress.IPv4Address`
            The ip address parameter.

        Returns
        -------
        An EntryIpAsDatabase object of the matched entry in the database.

        Raises
        ------
        ValueError
            If the binary search auxiliary method raises a ValueError exception. IN particular it is impossible to
            instantiate a valid Ipv4Address from an entry of the .tsv database.
            If the matched entry is formatted wrongly, not as described in https://iptoasn.com/. In particular one of
            3 errors occurred:
                - the start_ip_range is not a valid ip address
                - the end_ip_range is not a valid ip address
                - the as_number is not a valid integer number
        AutonomousSystemNotFoundError
            If there is no Autonomous System that match the ip parameter.
        """
        try:
            index = IpAsDatabase.binary_search(self.entries, ip)
        except ValueError:
            raise ValueError(f"!!! Database is file is not well-formatted !!!")
        if index == -1:
            raise AutonomousSystemNotFoundError(ip.exploded)
        else:
            try:
                tmp = EntryIpAsDatabase(self.entries[index])
                return tmp
            except ValueError:
                raise

    @staticmethod
    def binary_search(array_entries: List[StringEntryIpAsDatabase], ip_param: ipaddress.IPv4Address) -> int:
        """
        Auxiliary method that is concerned to implement binary search approach in the resolve method above.

        Parameters
        ----------
        array_entries : `list[StringEntryIpAsDatabase]`
            All the entries.
        ip_param : `ipaddress.IPv4Address`
            The ip parameter.

        Returns
        -------
        The corresponding index of the entry matched in array_entries.

        Raises
        ------
        ValueError
            An entry of the database is not well-formatted as described in https://iptoasn.com/.
        """
        inf = 0
        sup = len(array_entries) - 1
        while inf <= sup and (sup - inf) > 3:
            med = (inf + sup) // 2
            try:
                if ipaddress.ip_address(array_entries[med].start_ip_range) < ip_param:
                    inf = med + 1
                elif ipaddress.ip_address(array_entries[med].start_ip_range) > ip_param:
                    sup = med - 1
                else:
                    return med
            except ValueError:
                raise
        for i in range(inf, sup):
            if network_utils.is_in_ip_range(ip_param, ipaddress.ip_address(array_entries[i].start_ip_range), ipaddress.ip_address(array_entries[i].end_ip_range)):
                return i
        return -1

    def load(self):
        """
        Auxiliary method that is concerned to populate the entries attribute from the .tsv file database.

        Raises
        ------
        ValueError
            An entry of the database is not well-formatted as described in https://iptoasn.com/.
        """
        with open(self.filepath, "r", encoding='utf-8') as f:        # FileNotFoundError
            rd = csv.reader(f, delimiter=self.column_separator, quotechar='"')
            for row in rd:
                try:
                    entry = StringEntryIpAsDatabase(row)
                    self.entries.append(entry)
                except ValueError:
                    pass
            f.close()
