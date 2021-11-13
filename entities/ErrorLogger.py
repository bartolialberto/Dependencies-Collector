import csv
from pathlib import Path
from entities.TypesRR import TypesRR
from utils import file_utils, csv_utils


class ErrorEntry:
    """
    This class represent an entry in An ErrorLogger object.

    ...

    Instance Attributes
    -------------------
    domain_name : `str`
        The domain name associated with the error occurred.
    type : `TypesRR` or `str`
        The resource record type associated with the error occurred.
    reason_phrase : `str`
        A brief reason phrase of the error occurred.
    """

    def __init__(self, name: str, type_rr: TypesRR or str, error_message: str):
        """
        Instantiate an ErrorEntry initializing all the attributes defined above.

        :param name: The domain name.
        :type name: str
        :param type_rr: The resource record type.
        :type type_rr: TypesRR or str
        :param error_message: The reason phrase.
        :type error_message: str
        """
        self.domain_name = name
        self.type = type_rr
        self.reason_phrase = error_message

    def __eq__(self, other):
        if isinstance(other, ErrorEntry):
            return self.domain_name == other.domain_name
        else:
            return False


class ErrorLogger:
    """
    This class represent a simple sort of personalized Logger that keep tracks of all errors occurred in a list.

    ...

    Instance Attributes
    -------------------
    logs : `list[ErrorEntry]`
        The list of entries associated with errors occurred.
    separator : `str`
        The character separator between all the attributes of an ErrorEntry object, used when logs is exported to file.
    """

    def __init__(self, separator="\t"):
        """
        Instantiate an ErrorLogger initializing all the attributes defined above. You can set a personalized separator.

        :param separator: The character separator used when exporting the file. Default is TAB (\t).
        :type separator: str
        """
        self.logs = list()
        self.separator = separator

    def add_entry(self, entry: ErrorEntry) -> None:
        """
        Adds an ErrorEntry.

        :param entry: The ErrorEntry.
        :type entry: ErrorEntry
        """
        self.logs.append(entry)

    def set_separator(self, separator: str) -> None:
        """
        Set the separator.

        :param separator: The character separator.
        :type separator: str
        """
        self.separator = separator

    def write_to_csv(self, filepath: str) -> None:
        """
        Export logs in the list to a .csv file described by a filepath.

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
                for log in self.logs:
                    temp_list = list()
                    temp_list.append(log.domain_name)
                    temp_list.append(str(log.type))  # .to_string() solo se è typeRR
                    temp_list.append(log.reason_phrase)
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
        Export logs in the list to a .txt file described by a filepath.

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
                for log in self.logs:
                    f.write(
                        f"{log.domain_name}{self.separator}{str(log.type)}{self.separator}{log.reason_phrase}{self.separator}")  # .to_string() solo se è typeRR
                if len(self.logs) == 0:
                    f.write("No errors occurred.")
                f.close()
                f.close()
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise

    def write_to_csv_in_output_folder(self, filename="error_logs", project_root_directory=Path.cwd()) -> None:
        """
        Export the logs in the list to a .csv file in the output folder of the project directory. It uses the separator
        set to separate every attribute of the entry.
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
        (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
        returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
        return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
        to default as if the entry point is main.py file (which is the only entry point considered).

        :param filename: The personalized filename without extension, default is error_logs.
        :type filename: str
        :param project_root_directory: The Path object pointing at the project root directory.
        :type project_root_directory: Path
        :raise PermissionError: If filepath points to a directory.
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

    def write_to_txt_in_output_folder(self, filename="error_logs", project_root_directory=Path.cwd()) -> None:
        """
        Export the logs in the list to a .txt file in the output folder of the project directory. It uses the separator
        set to separate every attribute of the entry.

        :param filename: The personalized filename without extension, default is error_logs.
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

    def merge_from(self, other: 'ErrorLogger') -> None:       # FORWARD DECLARATIONS (REFERENCES)
        """
        Method that takes another ErrorLogger object and adds (without duplicates) all the logs from the other object
        to this (self object).

        :param other: Another ErrorLogger object.
        :type other: ErrorLogger
        """
        for record in other.logs:
            if record not in self.logs:
                self.logs.append(record)
