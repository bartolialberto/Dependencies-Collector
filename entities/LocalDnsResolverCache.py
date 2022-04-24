import csv
from collections import defaultdict
from ipaddress import IPv4Address
from pathlib import Path as PPath
from typing import List, Dict, Iterable
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
    cache: Dict[DomainName, Dict[TypesRR, RRecord]]
    separator: str

    def __init__(self, separator=";"):
        """
        Instantiate a LocalResolverCache initializing all the attributes defined above. You can set a personalized
        separator.

        :param separator: The character separator used when exporting the file. Default is a comma (;).
        :type separator: str
        """
        self.cache = defaultdict(dict)
        self.separator = separator

    def add_entry(self, entry: RRecord) -> None:
        """
        Adds a resource record.

        :param entry: The resource record.
        :type entry: RRecord
        :param control_for_no_duplicates: Optional flag to set if the duplicates control should execute for all cache
        :type control_for_no_duplicates: bool
        """
        self.cache[entry.name][entry.type] = entry

    def add_entries(self, entries: Iterable[RRecord]) -> None:
        """
        Adds multiple resource records.

        :param entries: The resource record list.
        :type entries: List[RRecord]
        :param control_for_no_duplicates: Optional flag to set if the duplicates control should execute for all cache
        :type control_for_no_duplicates: bool
        """
        for entry in entries:
            self.cache[entry.name][entry.type] = entry

    def add_path(self, path: Path) -> None:
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
        self.cache.clear()

    def lookup(self, domain_name: DomainName, type_rr: TypesRR) -> RRecord:
        """
        Search for the first occurrence of a resource record of name and type as parameters told.

        :param domain_name: The domain name.
        :type domain_name: DomainName
        :param type_rr: The resource record type.
        :type type_rr: TypesRR
        :raises NoRecordInCacheError: If there is no resource record satisfying the parameters in cache list.
        :returns: The first occurrence of name and resource record type as parameters told.
        :rtype: RRecord
        """
        try:
            return self.cache[domain_name][type_rr]
        except KeyError:
            raise NoRecordInCacheError(domain_name.string, type_rr)

    def resolve_path(self, domain_name: DomainName, rr_type_wanted: TypesRR) -> Path:
        """
        This method resolves the path from the domain name parameter to a RR of the TypesRR parameter.
        It returns the final RR and all the alias along the access path.
        There is also a boolean flag that decides to return all the aliases as RRs or simple strings. When returning as
        strings the name parameter is removed, so the list start with an alias.

        :param domain_name: The domain name.
        :type domain_name: DomainName
        :param rr_type_wanted: The RR type to be searched.
        :type rr_type_wanted: TypesRR
        :raise NoAvailablePathError: If there is not an access path.
        :return: The resolution RR and the list of aliases as a tuple.
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
        :param result: Is a parameter that populates with each recursive invocation.
        :type result: None or List[RRecord]
        :return: The access path.
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
                    self.add_entry(rr)
                except ValueError:
                    pass
                except NotResourceRecordTypeError:
                    pass
            f.close()
            if take_snapshot:
                self.take_temp_snapshot()
        except (ValueError, PermissionError, FileNotFoundError, OSError):
            raise

    def load_csv_from_output_folder(self, filename='dns_cache', take_snapshot=True, project_root_directory=PPath.cwd()) -> None:
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
        Export the cache in the list to a .csv file described by a filepath.

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
                for dn in self.cache.keys():
                    for rr in self.cache[dn].values():
                        temp_list = list()
                        temp_list.append(rr.name)
                        temp_list.append(rr.type.to_string())
                        temp_list.append(resource_records_utils.stamp_values(rr.type, rr.values))
                        writer.writerow(temp_list)
                f.close()
        except (PermissionError, FileNotFoundError, OSError):
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
        file = PPath(filepath)
        file_abs_path = str(file)
        try:
            with open(file_abs_path, 'w') as f:  # 'w' or 'x'
                for dn in self.cache.keys():
                    for rr in self.cache[dn].values():
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

    def write_to_csv_in_output_folder(self, filename="dns_cache", project_root_directory=PPath.cwd()) -> None:
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
        file = file_utils.set_file_in_folder(OUTPUT_FOLDER_NAME, filename+".csv", project_root_directory)
        file_abs_path = str(file)
        try:
            self.write_to_csv(file_abs_path)
        except (PermissionError, FileNotFoundError, OSError):
            raise

    def write_to_txt_in_output_folder(self, filename="dns_cache", project_root_directory=PPath.cwd()) -> None:
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
        file = file_utils.set_file_in_folder(OUTPUT_FOLDER_NAME, filename+".txt", project_root_directory)
        file_abs_path = str(file)
        try:
            self.write_to_txt(file_abs_path)
        except (PermissionError, FileNotFoundError, OSError):
            raise

    def take_temp_snapshot(self, project_root_directory=PPath.cwd()) -> None:
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
        file = file_utils.set_file_in_folder(SNAPSHOTS_FOLDER_NAME, "dns_cache.csv", project_root_directory=project_root_directory)
        if not file.exists():
            pass
        with file.open('w', encoding='utf-8', newline='') as f:
            write = csv.writer(f, dialect=csv_utils.return_personalized_dialect_name(f"{self.separator}"))
            for dn in self.cache.keys():
                for rr in self.cache[dn].values():
                    temp_list = list()
                    temp_list.append(rr.name.string)
                    temp_list.append(rr.type.to_string())
                    tmp = "["
                    for index, val in enumerate(rr.values):
                        if isinstance(val, DomainName):
                            tmp += val.string
                        elif isinstance(val, IPv4Address):
                            tmp += val.exploded
                        else:
                            raise ValueError
                        if not index == len(rr.values) - 1:
                            tmp += ","
                    tmp += "]"
                    temp_list.append(tmp)
                    write.writerow(temp_list)
            f.close()
