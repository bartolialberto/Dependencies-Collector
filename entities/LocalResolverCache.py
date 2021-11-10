import csv
from pathlib import Path
from typing import List
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from exceptions.NotResourceRecordTypeError import NotResourceRecordTypeError
from utils import file_utils
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from exceptions.NoRecordInCacheError import NoRecordInCacheError


class LocalResolverCache:
    """
    This class represent a simple sort of personalized Cache that keep tracks of all resource records in a list.

    ...

    Attributes
    ----------
    cache : `list[RRecord]`
        The list of resource records.
    separator : `str`
        The character separator between all the attributes of a Resource Record object, used when logs is exported to
        file.
    """
    cache: List[RRecord]
    separator: str

    def __init__(self, separator="\t"):     # \t = TAB
        """
        Instantiate a LocalResolverCache initializing all the attributes defined above. You can set a personalized
        separator.

        Parameters
        ----------
        separator : `str`, optional
            The character separator used when exporting the file. Default is TAB (\t).
        """
        self.cache = list()
        self.separator = separator

    def add_entry(self, entry: RRecord) -> None:
        """
        Adds a resource record.

        Parameters
        ----------
        entry : `RRecord`
            The resource record.
        """
        self.cache.append(entry)

    def set_separator(self, separator: str):
        """
        Set the separator.

        Parameters
        ----------
        separator : `str`
            The character separator.
        """
        self.separator = separator

    def look_up_first(self, domain_name: str, type_rr: TypesRR) -> RRecord:
        """
        Search for the first occurrence of a resource record of name and type as parameters told.

        Parameters
        ----------
        domain_name : `str`
            The domain name.
        type_rr : `TypesRR`
            The resource record type.

        Returns
        -------
        rr : `RRecord`
            The first occurrence of name and resource record type as parameters told.

        Raises
        ------
        NoRecordInCacheError
            If there is no resource record satisfying the parameters in cache list.
        """
        for rr in self.cache:
            if rr.name == domain_name and rr.type.to_string() == type_rr.to_string():
                return rr
        raise NoRecordInCacheError(domain_name, type_rr)

    def look_up(self, domain_name: str, type_rr: TypesRR) -> List[RRecord]:
        """
        Search for all occurrences of resource records of name and type as parameters told.

        Parameters
        ----------
        domain_name : `str`
            The domain name.
        type_rr : `TypesRR`
            The resource record type.

        Returns
        -------
        result : `list[RRecord]`
            A list containing all occurrences of name and resource record type as parameters told.

        Raises
        ------
        NoRecordInCacheError
            If there is no resource record satisfying the parameters in cache list.
        """
        result = []
        for rr in self.cache:
            if rr.name == domain_name and rr.type.to_string() == type_rr.to_string():
                result.append(rr)
        if len(result) == 0:
            raise NoRecordInCacheError(domain_name, type_rr)
        else:
            return result

    def load_csv(self, path: str) -> None:
        """
        Method that load from a .csv all the entries in this object cache list. More specifically, this method load the
        .csv file from a filepath (absolute or relative).

        Parameters
        ----------
        path : `str`
            Path of file to load, as absolute or relative path.

        Raises
        ------
        ValueError
            If it is impossible to parse a resource record from a line in the .csv file.
        FileNotFoundError
            If it is impossible to open the file.
        OSError
            If a general I/O error occurs.
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
        except FileNotFoundError:
            raise
        except OSError:
            raise

    def load_csv_from_output_folder(self, project_root_directory: Path) -> None:
        """
        Method that load from a .csv all the entries in this object cache list. More specifically, this method load the
        .csv file from the output folder of the project root directory. So just invoking this method will load the cache
        (if) exported from the previous execution.

        Parameters
        ----------
        project_root_directory : `Path`
            Path of the project root, findable through Path.cwd() of this package (directory).

        Raises
        ------
        ValueError
            If it is impossible to parse a resource record from a line in the .csv file.
        FileNotFoundError
            If it is impossible to open the file.
        OSError
            If a general I/O error occurs.
        """
        file = None
        try:
            result = file_utils.search_for_filename_in_subdirectory(project_root_directory, "output", "cache.csv")
            file = result[0]
        except FileWithExtensionNotFoundError:
            raise
        try:
            f = open(str(file), "r")
            for line in f:
                try:
                    rr = RRecord.parse_from_csv_entry_as_str(line)
                    self.cache.append(rr)
                except ValueError:
                    pass
                except NotResourceRecordTypeError:
                    pass
            f.close()
        except FileNotFoundError:
            raise
        except OSError:
            raise

    def write_to_csv_file(self, filename="cache") -> None:
        """
        Export the cache in the list to a .csv file in the output folder of the project directory. It uses the separator
        set to separate every attribute of the resource record.

        Parameters
        ----------
        filename : `str`, optional
            The personalized filename without extension, default is cache.
        """
        file = file_utils.set_file_in_folder(Path.cwd().parent, "output", filename+".txt")
        file_abs_path = str(file)
        with file.open('w', encoding='utf-8', newline='') as f:
            write = csv.writer(f)
            for rr in self.cache:
                temp_list = []
                temp_list.append(rr.name)
                temp_list.append(rr.type.to_string())
                tmp = "["
                for index, val in enumerate(rr.values):
                    tmp += val
                    if not index == len(rr.values) - 1:
                        tmp += ","
                tmp += "]"
                tmp.strip('"')      # TODO: non so perché ma viene scritto anche il carattere " se la lista contiene più di un elemento
                temp_list.append(tmp)
                write.writerow(temp_list)
            f.close()
            print(f".csv file '{file_abs_path}' successfully exported.")

    def write_to_txt_file(self, filename="cache") -> None:
        """
        Export the cache in the list to a .txt file in the output folder of the project directory. It uses the separator
        set to separate every attribute of the resource record.

        Parameters
        ----------
        filename : `str`, optional
            The personalized filename without extension, default is cache.
        """
        file = file_utils.set_file_in_folder(Path.cwd().parent, "output", filename+".txt")
        file_abs_path = str(file)
        with open(file_abs_path, 'w') as f:       # 'w' or 'x'
            for rr in self.cache:
                temp = f"{rr.name}{self.separator}{rr.type.to_string()}{self.separator}["
                for index, val in enumerate(rr.values):
                    temp += val
                    if not index == len(rr.values) - 1:
                        temp += " "
                temp += "]\n"
                f.write(temp)
            f.close()
            print(f".txt file '{file_abs_path}' successfully exported.")

    def merge_from(self, other: 'LocalResolverCache') -> None:       # FORWARD DECLARATIONS (REFERENCES)
        """
        Method that takes another LocalResolverCache object and adds (without duplicates) all the resource records from
        the other object cache to this (self object).

        Parameters
        ----------
        other : `LocalResolverCache`
            Another LocalResolverCache object.
        """
        for record in other.cache:
            if record not in self.cache:
                self.cache.append(record)
