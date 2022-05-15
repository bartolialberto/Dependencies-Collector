import csv
from ipaddress import IPv4Address
from pathlib import Path as PPath
from typing import Iterable, List
from entities.DomainName import DomainName
from entities.paths.PathBuilder import PathBuilder
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NotResourceRecordTypeError import NotResourceRecordTypeError
from exceptions.ReachedMaximumRecursivePathThresholdError import ReachedMaximumRecursivePathThresholdError
from static_variables import OUTPUT_FOLDER_NAME, SNAPSHOTS_FOLDER_NAME
from utils import file_utils, csv_utils, resource_records_utils
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.NoRecordInCacheError import NoRecordInCacheError
from entities.paths import Path


class LocalDnsResolverCache:
    """
    This class represents a simple sort of personalized cache that keep tracks of all resource records. Resource records
    are saved in 4 dictionaries, one for each resource records type; considered these data structures, duplicates of
    same resource records are not allowed.

    ...

    Instance Attributes
    -------------------
    cname_dict : Dict[DomainName, RRecord]
        Data structure containing all CNAME resource records.
    a_dict : Dict[DomainName, RRecord]
        Data structure containing all A resource records.
    ns_dict : Dict[DomainName, RRecord]
        Data structure containing all NS resource records.
    mx_dict : Dict[DomainName, RRecord]
        Data structure containing all MX resource records.
    separator : str
        The character separator between all the attributes of a Resource Record object, used when logs are exported to
        file.
    """
    def __init__(self, separator=";"):
        """
        Instantiate the object initializing all the attributes defined above. You can set a personalized separator.

        :param separator: The character separator used when exporting the file. Default is a comma (;).
        :type separator: str
        """
        self.cname_dict = dict()
        self.a_dict = dict()
        self.ns_dict = dict()
        self.mx_dict = dict()
        self.separator = separator

    def add_entry(self, entry: RRecord) -> None:
        """
        Adds a resource record.

        :param entry: The resource record.
        :type entry: RRecord
        """
        if entry.type == TypesRR.CNAME:
            self.cname_dict[entry.name] = entry
        elif entry.type == TypesRR.A:
            self.a_dict[entry.name] = entry
        elif entry.type == TypesRR.NS:
            self.ns_dict[entry.name] = entry
        elif entry.type == TypesRR.MX:
            self.mx_dict[entry.name] = entry
        else:
            raise ValueError

    def add_entries(self, entries: Iterable[RRecord]) -> None:
        """
        Adds multiple resource records.

        :param entries: The resource records collection.
        :type entries: Iterable[RRecord]
        """
        for entry in entries:
            self.add_entry(entry)

    def add_path(self, path: Path) -> None:
        """
        Adds all resource records associated to the Path object parameter.

        :param path: Path object.
        :return: Path
        """
        for rr in path:
            self.add_entry(rr)

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
        self.cname_dict.clear()
        self.a_dict.clear()
        self.ns_dict.clear()
        self.mx_dict.clear()

    def lookup(self, domain_name: DomainName, type_rr: TypesRR) -> RRecord:
        """
        Search for the occurrence of a resource record with name and type values as parameters ones.

        :param domain_name: The domain name.
        :type domain_name: DomainName
        :param type_rr: The resource record type.
        :type type_rr: TypesRR
        :raises NoRecordInCacheError: If there is no resource record satisfying the parameters in cache.
        :returns: Occurrence of name and resource record type values as parameters ones.
        :rtype: RRecord
        """
        if type_rr == TypesRR.CNAME:
            try:
                return self.cname_dict[domain_name]
            except KeyError:
                pass
        elif type_rr == TypesRR.A:
            try:
                return self.a_dict[domain_name]
            except KeyError:
                pass
        elif type_rr == TypesRR.NS:
            try:
                return self.ns_dict[domain_name]
            except KeyError:
                pass
        elif type_rr == TypesRR.MX:
            try:
                return self.mx_dict[domain_name]
            except KeyError:
                pass
        raise NoRecordInCacheError(domain_name.string, type_rr)

    def resolve_path(self, domain_name: DomainName, rr_type_wanted: TypesRR) -> Path:
        """
        This method resolves the path from the domain name parameter to a RR of the TypesRR parameter.

        :param domain_name: The domain name.
        :type domain_name: DomainName
        :param rr_type_wanted: The RR type to be searched.
        :type rr_type_wanted: TypesRR
        :raise NoAvailablePathError: If there is no such path.
        :return: The resulting path.
        :rtype: Path
        """
        try:
            inner_result = self.__inner_resolve_path(domain_name, rr_type_wanted, path_builder=None)
        except (NoAvailablePathError, ReachedMaximumRecursivePathThresholdError):
            raise
        return inner_result

    def __inner_resolve_path(self, domain_name: DomainName, rr_type_resolution: TypesRR, path_builder=None, count_invocations_threshold=100, count_invocations=1) -> Path:
        """
        This method is the real resolver for the path of a domain name. It's recursive.

        :param domain_name: The domain name.
        :type domain_name: DomainName
        :param rr_type_resolution: The RR type to be searched that resolves the path.
        :type rr_type_resolution: TypesRR
        :param path_builder: PathBuilder object carried through all invocations and used for the final result. None
        value is used for the initial invocation ('recursive initial seed').
        :type path_builder: Optional[PathBuilder]
        :param count_invocations_threshold: Number of invocation threshold to set the maximum number of recursive
        invocations allowed before raising an exception.
        :type count_invocations_threshold: int
        :param count_invocations: Current number of method's invocation.
        :type count_invocations: int
        :return: The resulting path.
        :rtype: Path
        """
        if path_builder is not None:
            pass
        else:
            path_builder = PathBuilder()
        count_invocations = count_invocations + 1
        if count_invocations >= count_invocations_threshold:
            raise ReachedMaximumRecursivePathThresholdError(domain_name.string)
        try:
            rr_a = self.lookup(domain_name, rr_type_resolution)
            path_builder.complete_resolution(rr_a)
            return path_builder.build()
        except NoRecordInCacheError:
            try:
                rr_cname = self.lookup(domain_name, TypesRR.CNAME)
                path_builder.add_cname(rr_cname)
                return self.__inner_resolve_path(rr_cname.get_first_value(), rr_type_resolution, path_builder=path_builder, count_invocations_threshold=count_invocations_threshold, count_invocations=count_invocations)
            except NoRecordInCacheError:
                raise NoAvailablePathError(domain_name.string)

    def __len__(self) -> int:
        """
        Return the length (the number of items) of this object.

        :return: Object length.
        :rtype: int
        """
        return len(self.cname_dict.values()) + len(self.a_dict.values()) + len(self.ns_dict.values()) + len(self.mx_dict.values())

    def load_csv(self, path: str, take_snapshot=True) -> None:
        """
        Method that loads from a .csv all the entries in this object cache. More specifically, this method loads the
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
                    self.add_entry(rr)
                except (ValueError, NotResourceRecordTypeError):
                    pass
            f.close()
            if take_snapshot:
                self.take_temp_snapshot()
        except (ValueError, PermissionError, FileNotFoundError, OSError):
            raise

    def load_csv_from_output_folder(self, filename='dns_cache', take_snapshot=True, project_root_directory=PPath.cwd()) -> None:
        """
        Method that loads from a .csv all the entries in this object cache. More specifically, this method loads the
        'dns_cache.csv' file from the output folder of the project root directory (PRD). So just invoking this method
        will load the cache (if) exported from the previous execution.
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we start the application from the main.py file in the PRD, every time Path.cwd() is encountered
        (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
        returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
        return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
        to default as if the entry point is main.py file (which is the only entry point considered).

        :param filename: Name of the cache file without extension. Default is 'dns_cache'.
        :type filename: str
        :param take_snapshot: Flag that sets up the SNAPSHOT folder and creates a temporary snapshot.
        :type take_snapshot: bool
        :param project_root_directory: Path of the project root.
        :type project_root_directory: Path
        :raise FilenameNotFoundError: If file with such filename doesn't exist.
        :raises ValueError: If it is impossible to parse a resource record from a line in the .csv file.
        :raise PermissionError: If filepath points to a directory.
        :raises FileNotFoundError: If it is impossible to open the file.
        :raises OSError: If a general I/O error occurs.
        """
        try:
            result = file_utils.search_for_filename_in_subdirectory(OUTPUT_FOLDER_NAME, filename+".csv", project_root_directory)
            file = result[0]
        except FilenameNotFoundError:
            raise
        try:
            self.load_csv(str(file), take_snapshot=take_snapshot)
        except (ValueError, PermissionError, FileNotFoundError, OSError):
            raise

    def write_to_csv(self, filepath: str) -> None:
        """
        Export cache to a .csv file described by a filepath.

        :param filepath: Path of file to write, as absolute or relative path.
        :type filepath: str
        :raise PermissionError: If filepath points to a directory.
        :raises FileNotFoundError: If it is impossible to open the file.
        :raises OSError: If a general I/O error occurs.
        """
        file = PPath(filepath)
        try:
            with file.open('w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, dialect=f'{csv_utils.return_personalized_dialect_name(self.separator)}')
                # writer.writerow(['', '', ''])       # .csv headers

                def csv_row(res: RRecord) -> List[DomainName, TypesRR, str]:
                    lst = list()
                    lst.append(res.name)
                    lst.append(res.type.to_string())
                    lst.append(resource_records_utils.stamp_values(res.type, res.values))
                    return lst

                for rr in self.cname_dict.values():
                    writer.writerow(csv_row(rr))
                for rr in self.a_dict.values():
                    writer.writerow(csv_row(rr))
                for rr in self.ns_dict.values():
                    writer.writerow(csv_row(rr))
                for rr in self.mx_dict.values():
                    writer.writerow(csv_row(rr))
                f.close()
        except (PermissionError, FileNotFoundError, OSError):
            raise

    def write_to_csv_in_output_folder(self, filename="dns_cache", project_root_directory=PPath.cwd()) -> None:
        """
        Export the cache in the list to a .csv file in the output folder of the project directory (if set correctly).
        It uses the separator set to separate every attribute of the resource record.
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we start the application from the main.py file in the PRD, every time Path.cwd() is encountered
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
        file = file_utils.set_file_in_folder(OUTPUT_FOLDER_NAME, filename+".csv", project_root_directory)
        file_abs_path = str(file)
        try:
            self.write_to_csv(file_abs_path)
        except (PermissionError, FileNotFoundError, OSError):
            raise

    def take_temp_snapshot(self, project_root_directory=PPath.cwd()) -> None:
        """
        Method that copies the current state of the cache in the SNAPSHOTS folder.
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we start the application from the main.py file in the PRD, every time Path.cwd() is encountered
        (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
        returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
        return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
        to default as if the entry point is main.py file (which is the only entry point considered).

        :param project_root_directory: The Path object pointing at the project root directory.
        :type project_root_directory: Path
        """
        file = file_utils.set_file_in_folder(SNAPSHOTS_FOLDER_NAME, "dns_cache.csv", project_root_directory=project_root_directory)
        if not file.exists():
            pass
        with file.open('w', encoding='utf-8', newline='') as f:
            write = csv.writer(f, dialect=csv_utils.return_personalized_dialect_name(f"{self.separator}"))

            def str_csv_row(res: RRecord) -> List[str]:
                lst = list()
                lst.append(res.name.string)
                lst.append(res.type.to_string())
                tmp = "["
                for index, val in enumerate(res.values):
                    if isinstance(val, DomainName):
                        tmp += val.string
                    elif isinstance(val, IPv4Address):
                        tmp += val.exploded
                    else:
                        raise ValueError
                    if not index == len(res.values) - 1:
                        tmp += ","
                tmp += "]"
                lst.append(tmp)
                return lst

            for rr in self.cname_dict.values():
                write.writerow(str_csv_row(rr))
            for rr in self.a_dict.values():
                write.writerow(str_csv_row(rr))
            for rr in self.ns_dict.values():
                write.writerow(str_csv_row(rr))
            for rr in self.mx_dict.values():
                write.writerow(str_csv_row(rr))
            f.close()
