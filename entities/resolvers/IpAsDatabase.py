import csv
import ipaddress
from pathlib import Path
from typing import List, Tuple
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import file_utils


class EntryIpAsDatabase:
    """
    This class represent an entry in the database as describe in https://iptoasn.com/g.

    ...

    Attributes
    ----------
    start_ip_range : ipaddress.IPv4Address
        The start of the ip range. It's an ip address.
    end_ip_range : ipaddress.IPv4Address
        The end of the ip range. It's an ip address.
    as_number : int
        The Autonomous System number. It's a number.
    country_code : str
        Should be the country code.
    as_description : str
        Should be the Autonomous System brief description.
    """
    def __init__(self, entries_inline: List[str]):
        """
        Instantiate a EntryIpAsDatabase object from a list of string follow format described in
        https://iptoasn.com/; list probably split with a character separator from an entire single string.

        :param entries_inline: List of string to associate to each entity of the entry.
        :type entries_inline: List[str]
        :raises ValueError: If the number of entities is not correct (5).
        If entry.start_ip_range is not a valid ipaddress.Ipv4Address.
        If entry.end_ip_range is not a valid ipaddress.Ipv4Address.
        If entry.as_number is not a valid integer number.
        """
        if len(entries_inline) != 5:
            raise ValueError
        string_start_ip_range = entries_inline[0]
        string_end_ip_range = entries_inline[1]
        string_as_number = entries_inline[2]
        string_country_code = entries_inline[3]
        string_as_description = entries_inline[4]

        try:
            tmp = ipaddress.IPv4Address(string_start_ip_range)
            self.start_ip_range = tmp
        except ValueError:
            raise
        try:
            tmp = ipaddress.IPv4Address(string_end_ip_range)
            self.end_ip_range = tmp
        except ValueError:
            raise
        try:
            tmp = int(string_as_number)
            self.as_number = tmp
        except ValueError:
            raise
        self.country_code = string_country_code
        self.as_description = string_as_description

    def get_all_networks(self) -> List[ipaddress.IPv4Network]:
        """
        Returns a list of networks from the summarized network range given the first and last IP addresses of the range
        in the entry (self object).

        :raise TypeError: If first or last are not IP addresses or are not of the same version.
        :raise ValueError: If last is not greater than first or if first address version is not 4 or 6
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
        :raise TypeError: If first or last are not IP addresses or are not of the same version.
        :raise ValueError: If last is not greater than first or if first address version is not 4 or 6.
        If there's not a network in which is contained the ip address parameter.
        :returns: A tuple containing the belonging network first and then all the networks.
        :rtype: Tuple[ipaddress.IPv4Network, List[ipaddress.IPv4Network]]
        """
        try:
            networks = self.get_all_networks()
        except (TypeError, ValueError):
            raise
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
    This class represent an object that read the .tsv database inserted in the 'input' folder of the project root
    directory and provides the necessary methods to query such database to return a match with an Autonomous System.

    Attributes
    ----------
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
        :raise FileWithExtensionNotFoundError: If the database .tsv file is not found.
        :raise OSError: If is there a problem opening the .tsv file.
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
        :raise AutonomousSystemNotFoundError: If there is no Autonomous System that match the ip parameter.
        :raise ValueError: An entry of the database is not well-formatted as described in https://iptoasn.com/.
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
                return self.entries[index]
            except ValueError:
                raise

    @staticmethod
    def __binary_search(array_entries: List[EntryIpAsDatabase], ip_param: ipaddress.IPv4Address) -> int:
        """
        Auxiliary method that is concerned to implement binary search approach in the resolve method above.

        :param array_entries: All the entries.
        :type array_entries: List[StringEntryIpAsDatabase]
        :param ip_param: The ip parameter.
        :type ip_param: ipaddress.IPv4Address
        :raises ValueError: An entry of the database is not well-formatted as described in https://iptoasn.com/.
        :returns: The corresponding index of the entry matched in array_entries. It returns -1 if nothing is found.
        :rtype: int
        """
        inf = 0
        sup = len(array_entries) - 1
        while inf <= sup:
            if sup - inf <= 2:
                print('', end='')
                pass
            med = (inf + sup) // 2
            try:
                start = array_entries[med].start_ip_range
                end = array_entries[med].end_ip_range
                if end < ip_param:
                    inf = med + 1
                elif start > ip_param:
                    sup = med - 1
                else:
                    return med
            except ValueError:
                raise
        return -1

    def get_entry_from_as_number(self, as_number: int) -> EntryIpAsDatabase:
        """
        This method returns the database entry that matches the autonomous system associated with the parameter.
        The method needs to control every single entry, so it is pretty slow.

        :param as_number: The autonomous system number.
        :type as_number: int
        :raise AutonomousSystemNotFoundError: If no entry is found.
        :raise ValueError: If the matched entry is not well-formatted.
        :returns: An EntryIpAsDatabase object of the matched entry in the database.
        :rtype: EntryIpAsDatabase
        """
        for entry in self.entries:
            if int(entry.as_number) == as_number:
                try:
                    # return EntryIpAsDatabase(entry.as_number)
                    return entry
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
                    entry = EntryIpAsDatabase(row)
                    self.entries.append(entry)
                except ValueError:
                    pass
            f.close()
