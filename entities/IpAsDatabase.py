import csv
import ipaddress
from pathlib import Path
from typing import List, Tuple
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import network_utils
from utils import file_utils


class StringEntryIpAsDatabase:
    """
    This class represent the same entity as EntryIpAsDatabase, the only difference is that all attributes are string.
    This is done because the basic idea is:

    1- download the database (see https://iptoasn.com/) and put downloaded file in the input folder
    (in project root folder)

    2- instantiating an IpAsDatabase object will load all entries of the database in the entries attribute automatically
    because the code will navigate the input folder searching the first occurrence of a .tsv file.
    The entries attribute is a list of StringEntryIpAsDatabase and not EntryIpAsDatabase because the database will
    contain around half a million entries, so if we instantiate for every entry (entry == row) an
    EntryIpAsDatabase performance will be worse than instantiating a StringEntryIpAsDatabase. In this manner to
    resolve the ip parameter will require only an instantiation of the first ip address in the entry
    (start_ip_range as ipaddress.Ipv4Address object).

    3- only after the resolution of the ip address to an entry of the database, the entry is instantiated as a
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
        Should be the Autonomous System number (without starting 'AS')
    country_code : `str`
        Should be the country code
    as_description : `str`
        Should be the Autonomous System brief description
    """

    def __init__(self, entries_inline: List[str]):
        """
        Instantiate a StringEntryIpAsDatabase object from a list of string follow format described in
        https://iptoasn.com/; list probably split with a character separator from an entire single string.

        :param entries_inline: List of string to associate to each entity of the entry.
        :type entries_inline: List[str]
        :raises ValueError: If the number of entities is not correct (5).
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

    Instance Attributes
    -------------------
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

    def __init__(self, entry: StringEntryIpAsDatabase):
        """
        Instantiate a EntryIpAsDatabase object from a StringEntryIpAsDatabase object to emphasize the fact that an
        EntryIpAsDatabase object is used at the end of the research.

        :param entry: Corresponding StringEntryIpAsDatabase object.
        :type entry: StringEntryIpAsDatabase
        :raises ValueError: If entry.start_ip_range is not a valid ipaddress.Ipv4Address.
        If entry.end_ip_range is not a valid ipaddress.Ipv4Address.
        If entry.as_number is not a valid integer number.
        """
        try:
            tmp = ipaddress.IPv4Address(entry.start_ip_range)
            self.start_ip_range = tmp
        except ValueError:
            raise
        try:
            tmp = ipaddress.IPv4Address(entry.end_ip_range)
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

        :raises TypeError: If first or last are not IP addresses or are not of the same version.
        If last is not greater than first or if first address version is not 4 or 6
        :returns: A list of valid ipaddress.IPv4Network.
        :rtype: List[ipaddress.IPv4Network]
        """
        try:
            return list(ipaddress.summarize_address_range(self.start_ip_range, self.end_ip_range))
        except TypeError:
            raise       # if first or last are not IP addresses or are not of the same version
        except ValueError:
            raise       # if last is not greater than first or if first address version is not 4 or 6

    def get_network_of_ip(self, ip: ipaddress.IPv4Address) -> Tuple[ipaddress.IPv4Network, List[ipaddress.IPv4Network]]:
        """
        Return the network from the summarized network range given the first and last IP addresses of the range in the
        entry (self object), and all the networks associated with such range.

        :param ip: Ip address.
        :type ip: ipaddress.IPv4Address
        :raises ValueError: If there's not a network in which is contained the ip address parameter.
        :returns: A tuple containing the belonging network first and then all the newtorks.
        :rtype: Tuple[ipaddress.IPv4Network, List[ipaddress.IPv4Network]]
        """
        networks = self.get_all_networks()
        for network in networks:
            if ip in network:
                return network, networks
        raise ValueError()

    def __str__(self) -> str:
        return f"{str(self.start_ip_range)}\t{str(self.end_ip_range)}\t{str(self.as_number)}\t{self.country_code}\t{self.as_description}"

    def __eq__(self, other) -> bool:
        if isinstance(other, EntryIpAsDatabase):
            return self.as_number == other.as_number
        else:
            return False


class IpAsDatabase:
    """
    This class represent an object that read the .tsv database inserted in the input folder of the project directory
    and provides the necessary methods to query such database to return a match with an Autonomous System.

    Instance Attributes
    -------------------
    filepath : `str`
        If found, it is the absolute filepath of the .tsv database.
    column_separator : `str`
        The character separator between every column-value of each entry
    entries : `list[StringEntryIpAsDatabase]`
        If the database is valid, these are all the entries of the database.
    """

    def __init__(self, project_root_directory=Path.cwd(), column_separator='\t'):      # FileNotFoundError, '\t' = TAB
        """
        Instantiate an IpAsDatabase object setting the filepath of the .tsv database file and then the file is read
        in order to populate a list with all the database entries. You can set manually the separator used to separate
        the columns in the entry of the database, and the project root directory (PRD).
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
        (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
        returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
        return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
        to default as if the entry point is main.py file (which is the only entry point considered).

        :param project_root_directory: The Path object pointing at the project root directory.
        :type project_root_directory: Path
        :param column_separator: The character separator between every column-value of each entry
        :type column_separator: str
        :raises FileWithExtensionNotFoundError: If the database .tsv file is not found.
        """
        try:
            result = file_utils.search_for_file_type_in_subdirectory("input", ".tsv", project_root_directory)
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

        :param ip: The ip address parameter.
        :type ip: ipaddress.IPv4Address
        :raises ValueError: If the binary search auxiliary method raises a ValueError exception. In particular it is
        impossible to instantiate a valid Ipv4Address from an entry of the .tsv database.
        If the matched entry is formatted wrongly, not as described in https://iptoasn.com/. In particular one of 3
        errors occurred:
            - the start_ip_range is not a valid ip address
            - the end_ip_range is not a valid ip address
            - the as_number is not a valid integer number
        :raises AutonomousSystemNotFoundError: If there is no Autonomous System that match the ip parameter.
        :returns: An EntryIpAsDatabase object of the matched entry in the database.
        :rtype: EntryIpAsDatabase
        """
        try:
            index = IpAsDatabase.__binary_search(self.entries, ip)
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
    def __binary_search(array_entries: List[StringEntryIpAsDatabase], ip_param: ipaddress.IPv4Address) -> int:
        """
        Auxiliary method that is concerned to implement binary search approach in the resolve method above.

        :param array_entries: All the entries.
        :type array_entries: List[StringEntryIpAsDatabase]
        :param ip_param: The ip parameter.
        :type ip_param: ipaddress.IPv4Address
        :raises ValueError: An entry of the database is not well-formatted as described in https://iptoasn.com/.
        :returns: The corresponding index of the entry matched in array_entries.
        :rtype: int
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

    def get_entry_from_as_number(self, as_number: int) -> EntryIpAsDatabase:
        """
        Method return the database entry that matches the autonomous system associated with the parameter. Number
        obviously with the starting 'AS'. The method needs to control every single entry, so it is pretty slow.

        :param as_number: The autonomous system number.
        :type as_number: int
        :raises AutonomousSystemNotFoundError: If no entry is found.
        :raises ValueError: If the matched entry is not well-formatted.
        :returns: An EntryIpAsDatabase object of the matched entry in the database.
        :rtype: EntryIpAsDatabase
        """
        for entry in self.entries:
            if int(entry.as_number) == as_number:
                try:
                    return EntryIpAsDatabase(entry)
                except ValueError:
                    raise
        raise AutonomousSystemNotFoundError(as_number)

    def load(self):
        """
        Auxiliary method that is concerned to populate the entries attribute from the .tsv file database.

        :raises ValueError: An entry of the database is not well-formatted as described in https://iptoasn.com/.
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
