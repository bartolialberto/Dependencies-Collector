import csv
import ipaddress
from pathlib import Path
from typing import List, Set
from entities.EntryIpAsDatabase import EntryIpAsDatabase
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from static_variables import INPUT_FOLDER_NAME
from utils import file_utils


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

    def __init__(self, project_root_directory=Path.cwd(), column_separator='\t'):      # '\t' = TAB
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
            result = file_utils.search_for_file_type_in_subdirectory(INPUT_FOLDER_NAME, ".tsv", project_root_directory)
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

    def get_entries_from_as_number(self, as_number: int) -> Set[EntryIpAsDatabase]:
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
        entries = set()
        for entry in self.entries:
            if entry.as_number == as_number:
                entries.add(entry)
        if len(entries) == 0:
            raise AutonomousSystemNotFoundError(as_number)
        else:
            return entries

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
