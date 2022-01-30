import copy
import csv
from pathlib import Path
from typing import List, Set, Tuple
from entities.Zone import Zone
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NotResourceRecordTypeError import NotResourceRecordTypeError
from utils import file_utils, csv_utils, list_utils, domain_name_utils
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.NoRecordInCacheError import NoRecordInCacheError


class LocalDnsResolverCache:
    """
    This class represents a simple sort of personalized Cache that keep tracks of all resource records in a list.

    ...

    Instance Attributes
    -------------------
    cache : `list[RRecord]`
        The list of resource records.
    separator : `str`
        The character separator between all the attributes of a Resource Record object, used when logs are exported to
        file.
    """
    cache: List[RRecord]
    separator: str

    def __init__(self, separator=";"):
        """
        Instantiate a LocalResolverCache initializing all the attributes defined above. You can set a personalized
        separator.

        :param separator: The character separator used when exporting the file. Default is a comma (;).
        :type separator: str
        """
        self.cache = list()
        self.separator = separator

    def add_entry(self, entry: RRecord, control_for_no_duplicates=False) -> None:
        """
        Adds a resource record.

        :param entry: The resource record.
        :type entry: RRecord
        :param control_for_no_duplicates: Optional flag to set if the duplicates control should execute for all cache
        :type control_for_no_duplicates: bool
        """
        if control_for_no_duplicates:
            if entry not in self.cache:
                self.cache.append(entry)
        else:
            self.cache.append(entry)

    def add_entries(self, entries: List[RRecord], control_for_no_duplicates=False) -> None:
        """
        Adds multiple resource records.

        :param entries: The resource record list.
        :type entries: List[RRecord]
        :param control_for_no_duplicates: Optional flag to set if the duplicates control should execute for all cache
        :type control_for_no_duplicates: bool
        """
        if control_for_no_duplicates:
            for entry in entries:
                if entry not in self.cache:
                    self.cache.append(entry)
        else:
            for entry in entries:
                self.cache.append(entry)

    def set_separator(self, separator: str) -> None:
        """
        Sets the separator.

        :param separator: The character separator.
        :type separator: str
        """
        self.separator = separator

    def clear(self) -> None:
        """
        Cleans everything, deleting all the resource records.

        """
        self.cache.clear()

    def lookup_first(self, domain_name: str, type_rr: TypesRR) -> RRecord:
        """
        Search for the first occurrence of a resource record of name and type as parameters told.

        :param domain_name: The domain name.
        :type domain_name: str
        :param type_rr: The resource record type.
        :type type_rr: TypesRR
        :raises NoRecordInCacheError: If there is no resource record satisfying the parameters in cache list.
        :returns: The first occurrence of name and resource record type as parameters told.
        :rtype: RRecord
        """
        for rr in self.cache:
            if domain_name_utils.equals(rr.name, domain_name) and rr.type == type_rr:
                return rr
        raise NoRecordInCacheError(domain_name, type_rr)

    def lookup(self, domain_name: str, type_rr: TypesRR) -> List[RRecord]:
        """
        Search for all occurrences of resource records of name and type as parameters say.

        :param domain_name: The domain name.
        :type domain_name: str
        :param type_rr: The resource record type.
        :type type_rr: TypesRR
        :raises NoRecordInCacheError: If there is no resource record satisfying the parameters in cache list.
        :returns: A list containing all occurrences of name and resource record type as parameters told.
        :rtype: List[RRecord]
        """
        result = []
        for rr in self.cache:
            if domain_name_utils.equals(rr.name, domain_name) and rr.type == type_rr:
                result.append(rr)
        if len(result) == 0:
            raise NoRecordInCacheError(domain_name, type_rr)
        else:
            return result

    def lookup_first_name_from_alias(self, domain_name: str) -> RRecord:
        """
        Returns first CNAME RR in which the domain_name parameter is an alias.

        :param domain_name:
        :return:
        """
        for rr in self.cache:
            if rr.type == TypesRR.CNAME and domain_name_utils.is_contained_in_list(rr.values, domain_name):
                return rr
        raise NoRecordInCacheError(domain_name, TypesRR.CNAME)

    def lookup_from_list(self, names: List[str], type_rr: TypesRR) -> RRecord:
        """
        This method looks up the first resource record found in cache using all the name in the list parameter
        sequentially. Practically aggregates a simple look_up_first method for the first element in a list.

        :param names: List of domain names.
        :type names: List[str]
        :param type_rr:
        :type type_rr: TypesRR
        :return: The first resource record found from all the elements in the list sequentially.
        :rtype: RRecord
        """
        for name in names:
            try:
                return self.lookup_first(name, type_rr)
            except NoRecordInCacheError:
                pass
        raise NoRecordInCacheError(str(names), type_rr)

    def lookup_all_aliases(self, name: str) -> Set[str]:
        """
        This method, given a domain name, searches all the aliases associated with it in the cache: that means resource
        records with the domain name parameter as name, or resource records with contains the domain name parameter in
        the values field.

        :param name: The domain name.
        :type name: str
        :return: A set of all the aliases (as string) associated to the domain name parameter.
        :rtype: Set[str]
        """
        try:
            rr_a, aliases = self.resolve_path(name, TypesRR.A, as_string=True)
        except NoAvailablePathError:
            result = set()
            result.add(name)
            return result
        result = set(aliases)
        result.add(name)
        return result

    def resolve_path(self, domain_name: str, rr_type_wanted: TypesRR, as_string=True) -> Tuple[RRecord, List[str] or List[RRecord]]:
        """
        This method resolves the path from the domain name parameter to a RR of the TypesRR parameter.
        It returns the final RR and all the alias along the access path.
        There is also a boolean flag that decides to return all the aliases as RRs or simple strings. When returning as
        strings the name parameter is removed, so the list start with an alias.

        :param domain_name: The domain name.
        :type domain_name: str
        :param rr_type_wanted: The RR type to be searched.
        :type rr_type_wanted: TypesRR
        :param as_string: Flag to decide the list of aliases format.
        :param as_string: bool
        :raise NoAvailablePathError: If there is not an access path.
        :return: The resolution RR and the list of aliases as a tuple.
        :rtype: Tuple[RRecord, List[str] or List[RRecord]]
        """
        try:
            inner_result = self.__inner_resolve_path(domain_name, rr_type_wanted, result=None)
        except NoAvailablePathError:
            raise
        aliases = list()
        for rr in inner_result[0:-1]:
            if as_string:
                aliases.append(rr.get_first_value())
            else:
                aliases.append(rr)
        return inner_result[-1], aliases

    def __inner_resolve_path(self, domain_name: str, rr_type_resolution: TypesRR, result=None) -> List[RRecord]:
        """
        This method is the real resolver for the path of a domain name. It's recursive.

        :param domain_name: The domain name.
        :type domain_name: str
        :param rr_type_resolution: The RR type to be searched that resolves the path.
        :type rr_type_resolution: TypesRR
        :param result: Is a parameter that populates with each recursive invocation.
        :type result: None or List[RRecord]
        :return: The access path.
        :rtype: List[RRecord]
        """
        if result is None:
            result = list()
        else:
            pass
        try:
            rr_a = self.lookup_first(domain_name, rr_type_resolution)
            result.append(rr_a)
            return result
        except NoRecordInCacheError:
            try:
                rr_cname = self.lookup_first(domain_name, TypesRR.CNAME)
                result.append(rr_cname)
                return self.__inner_resolve_path(rr_cname.get_first_value(), rr_type_resolution, result=result)
            except NoRecordInCacheError:
                raise NoAvailablePathError(domain_name)

    def resolve_zone_object_from_zone_name(self, zone_name: str) -> Tuple[Zone, List[RRecord]]:
        """
        This method searches the Zone (the application-defined object) corresponding to the zone name parameter.
        It is 'constructed' searching for all the nameservers of the zone and the aliases.

        :param zone_name: The zone name.
        :type zone_name: str
        :raise NoRecordInCacheError: If there is no a NS RR corresponding to the zone name parameter.
        :raise NoAvailablePathError: If there is no access path for a name server of the zone.
        :return: The Zone (the application-defined object).
        :rtype: Zone
        """
        try:
            rr_ns, rr_cnames = self.resolve_path(zone_name, TypesRR.NS, as_string=False)
        except NoRecordInCacheError:
            raise
        try:
            zone = self.resolve_zone_from_ns_rr(rr_ns)
        except NoRecordInCacheError:
            raise
        for rr in rr_cnames:
            zone.zone_aliases.append(rr)
        return zone, rr_cnames

    def resolve_zone_from_ns_rr(self, rr_ns: RRecord) -> Zone:
        """
        This method searches the Zone (the application-defined object) corresponding to the RR parameter.
        It is 'constructed' searching for all the nameservers of the zone and the aliases.

        :param rr_ns: A NS type RR.
        :type rr_ns: RRecord
        :raise NoAvailablePathError: If there is no access path for a name server of the zone.
        :return: The Zone (the application-defined object).
        :rtype: Zone
        """
        result_zone_name = rr_ns.name
        result_zone_nameservers = list()
        result_zone_name_servers_cnames = list()
        result_zone_addresses = list()
        for nameserver in rr_ns.values:
            result_zone_nameservers.append(nameserver)
            try:
                rr_a, rr_cnames = self.resolve_path(nameserver, TypesRR.A, as_string=False)
            except NoAvailablePathError:
                raise
            for rr in rr_cnames:
                result_zone_name_servers_cnames.append(rr)
            result_zone_addresses.append(rr_a)
        return Zone(result_zone_name, result_zone_nameservers, result_zone_name_servers_cnames, result_zone_addresses, list())

    def resolve_zones_from_nameserver(self, nameserver: str) -> List[str]:
        """
        This method checks if the nameserver parameter is 'nameserver of the zone' of some zones in the cache.
        If it so, a list of zone names is returned.

        :param nameserver: A domain name.
        :type nameserver: str
        :return: A list of zone names that has such nameserver (or aliases associated to it) as 'nameserver of the zone'.
        :rtype: List[str]
        """
        result = []
        aliases = self.lookup_all_aliases(nameserver)
        for rr in self.cache:
            if rr.type == TypesRR.NS and domain_name_utils.is_contained_in_list(rr.values, nameserver):
                list_utils.append_with_no_duplicates(result, rr.name)
            else:
                for alias in aliases:
                    if rr.type == TypesRR.NS and domain_name_utils.is_contained_in_list(rr.values, alias):
                        list_utils.append_with_no_duplicates(result, rr.name)
                        break
        return result

    def load_csv(self, path: str, take_snapshot=True) -> None:
        """
        Method that load from a .csv all the entries in this object cache list. More specifically, this method load the
        .csv file from a filepath (absolute or relative). It provides an optional flag to copy the state of cache in a
        file for later consumption.

        :param path: Path of file to load, as absolute or relative path.
        :type path: str
        :param take_snapshot: Flag for keeping track of cache when errors occur.
        :type take_snapshot: bool
        :raise ValueError: If it is impossible to parse a resource record from a line in the .csv file.
        :raise PermissionError: If filepath points to a directory.
        :raise FileNotFoundError: If it is impossible to open the file.
        :raise OSError: If a general I/O error occurs.
        """
        try:
            f = open(path, "r")
            for line in f:
                try:
                    rr = RRecord.parse_from_csv_entry_as_str(line)
                    self.cache.append(rr)
                except ValueError:
                    pass
                except NotResourceRecordTypeError:
                    pass
            f.close()
            if take_snapshot:
                self.take_temp_snapshot()
        except ValueError:
            raise
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise

    def load_csv_from_output_folder(self, filename='dns_cache', project_root_directory=Path.cwd()) -> None:
        """
        Method that load from a .csv all the entries in this object cache list. More specifically, this method load the
        'dns_cache.csv' file from the output folder of the project root directory (if set correctly). So just invoking
        this method will load the cache (if) exported from the previous execution.
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
        (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
        returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
        return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
        to default as if the entry point is main.py file (which is the only entry point considered).

        :param filename: Name of the cache file without extension. Default is 'dns_cache'.
        :type filename: str
        :param project_root_directory: Path of the project root.
        :type project_root_directory: Path
        :raise FilenameNotFoundError: If file with such filename doesn't exist.
        :raises ValueError: If it is impossible to parse a resource record from a line in the .csv file.
        :raise PermissionError: If filepath points to a directory.
        :raises FileNotFoundError: If it is impossible to open the file.
        :raises OSError: If a general I/O error occurs.
        """
        file = None
        try:
            result = file_utils.search_for_filename_in_subdirectory("output", filename+".csv", project_root_directory)
            file = result[0]
        except FilenameNotFoundError:
            raise
        try:
            self.load_csv(str(file))
        except ValueError:
            raise
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise

    def write_to_csv(self, filepath: str) -> None:
        """
        Export the cache in the list to a .csv file described by a filepath.

        :param filepath: Path of file to write, as absolute or relative path.
        :type filepath: str
        :raise PermissionError: If filepath points to a directory.
        :raises FileNotFoundError: If it is impossible to open the file.
        :raises OSError: If a general I/O error occurs.
        """
        file = Path(filepath)
        try:
            with file.open('w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, dialect=f'{csv_utils.return_personalized_dialect_name(self.separator)}')
                for rr in self.cache:
                    temp_list = list()
                    temp_list.append(rr.name)
                    temp_list.append(rr.type.to_string())
                    tmp = "["
                    for index, val in enumerate(rr.values):
                        tmp += val
                        if not index == len(rr.values) - 1:
                            tmp += ","
                    tmp += "]"
                    temp_list.append(tmp)
                    writer.writerow(temp_list)
                f.close()
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise

    def write_to_txt(self, filepath: str) -> None:
        """
        Export the cache in the list to a .txt file described by a filepath.

        :param filepath: Path of file to write, as absolute or relative path.
        :type filepath: str
        :raise PermissionError: If filepath points to a directory.
        :raises FileNotFoundError: If it is impossible to open the file.
        :raises OSError: If a general I/O error occurs.
        """
        file = Path(filepath)
        file_abs_path = str(file)
        try:
            with open(file_abs_path, 'w') as f:  # 'w' or 'x'
                for rr in self.cache:
                    temp = f"{rr.name}{self.separator}{rr.type.to_string()}{self.separator}["
                    for index, val in enumerate(rr.values):
                        temp += val
                        if not index == len(rr.values) - 1:
                            temp += " "
                    temp += "]\n"
                    f.write(temp)
                f.close()
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise

    def write_to_csv_in_output_folder(self, filename="dns_cache", project_root_directory=Path.cwd()) -> None:
        """
        Export the cache in the list to a .csv file in the output folder of the project directory (if set correctly).
        It uses the separator set to separate every attribute of the resource record.
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
        (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
        returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
        return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
        to default as if the entry point is main.py file (which is the only entry point considered).

        :param filename: The personalized filename without extension, default is 'dns_cache'.
        :type filename: str
        :param project_root_directory: The Path object pointing at the project root directory.
        :type project_root_directory: Path
        :raises PermissionError: If filepath points to a directory.
        :raises FileNotFoundError: If it is impossible to open the file.
        :raises OSError: If a general I/O error occurs.
        """
        file = file_utils.set_file_in_folder("output", filename+".csv", project_root_directory)
        file_abs_path = str(file)
        try:
            self.write_to_csv(file_abs_path)
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise

    def write_to_txt_in_output_folder(self, filename="dns_cache", project_root_directory=Path.cwd()) -> None:
        """
        Export the cache in the list to a .txt file in the output folder of the project directory. It uses the separator
        set to separate every attribute of the resource record.
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
        (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
        returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
        return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
        to default as if the entry point is main.py file (which is the only entry point considered).

        :param filename: The personalized filename without extension, default is 'dns_cache'.
        :type filename: str
        :param project_root_directory: The Path object pointing at the project root directory.
        :type project_root_directory: Path
        :raises PermissionError: If filepath points to a directory.
        :raises FileNotFoundError: If it is impossible to open the file.
        :raises OSError: If a general I/O error occurs.
        """
        file = file_utils.set_file_in_folder("output", filename+".txt", project_root_directory)
        file_abs_path = str(file)
        try:
            self.write_to_txt(file_abs_path)
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise

    def merge_from(self, other: 'LocalDnsResolverCache') -> None:       # FORWARD DECLARATIONS (REFERENCES)
        """
        Method that takes another LocalResolverCache object and adds (without duplicates) all the resource records from
        the other object cache to this (self object).

        :param other: Another LocalResolverCache object.
        :type other: LocalDnsResolverCache
        """
        for record in other.cache:
            if record not in self.cache:
                self.cache.append(record)

    def take_temp_snapshot(self, project_root_directory=Path.cwd()) -> None:
        """
        Method that copies the current state of the cache list in the input folder.
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
        (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
        returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
        return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
        to default as if the entry point is main.py file (which is the only entry point considered).

        :param project_root_directory: The Path object pointing at the project root directory.
        :type project_root_directory: Path
        """
        file = file_utils.set_file_in_folder("SNAPSHOTS", "temp_dns_cache.csv", project_root_directory=project_root_directory)
        if not file.exists():
            pass
        with file.open('w', encoding='utf-8', newline='') as f:
            write = csv.writer(f, dialect=csv_utils.return_personalized_dialect_name(f"{self.separator}"))
            for rr in self.cache:
                temp_list = list()
                temp_list.append(rr.name)
                temp_list.append(rr.type.to_string())
                tmp = "["
                for index, val in enumerate(rr.values):
                    tmp += val
                    if not index == len(rr.values) - 1:
                        tmp += ","
                tmp += "]"
                temp_list.append(tmp)
                write.writerow(temp_list)
            f.close()
