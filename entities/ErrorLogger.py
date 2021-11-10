import csv
from pathlib import Path
from typing import List
from entities.TypesRR import TypesRR
from utils import file_utils


class ErrorEntry:
    """
    This class represent an entry in An ErrorLogger object.

    ...

    Attributes
    ----------
    domain_name : `str`
        The domain name associated with the error occurred.
    type : `TypesRR` or `str`
        The resource record type associated with the error occurred.
    reason_phrase : `str`
        A brief reason phrase of the error occurred.
    """
    domain_name: str
    type: TypesRR or str
    reason_phrase: str

    def __init__(self, name: str, type_rr: TypesRR or str, error_message: str):
        """
        Instantiate an ErrorEntry initializing all the attributes defined above.

        Parameters
        ----------
        name : `str`
            The domain name.
        type_rr : `TypesRR` or `str`
            The resource record type.
        error_message : `str`
            The reason phrase.
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

    Attributes
    ----------
    logs : `list[ErrorEntry]`
        The list of entries associated with errors occurred.
    separator : `str`
        The character separator between all the attributes of an ErrorEntry object, used when logs is exported to file.
    """
    logs: List[ErrorEntry]
    separator: str

    def __init__(self, separator="\t"):
        """
        Instantiate an ErrorLogger initializing all the attributes defined above. You can set a personalized separator.

        Parameters
        ----------
        separator : `str`, optional
            The character separator used when exporting the file. Default is TAB (\t).
        """
        self.logs = list()
        self.separator = separator

    def add_entry(self, entry: ErrorEntry) -> None:
        """
        Adds an ErrorEntry.

        Parameters
        ----------
        entry : `ErrorEntry`
            The ErrorEntry.
        """
        self.logs.append(entry)

    def set_separator(self, separator: str) -> None:
        """
        Set the separator.

        Parameters
        ----------
        separator : `str`
            The character separator.
        """
        self.separator = separator

    def write_to_csv_file(self, filename="error_logs") -> None:
        """
        Export the logs in the list to a .csv file in the output folder of the project directory. It uses the separator
        set to separate every attribute of the entry.

        Parameters
        ----------
        filename : `str`, optional
            The personalized filename without extension, default is error_logs.
        """
        file = file_utils.set_file_in_folder(Path.cwd().parent, "output", filename+".txt")
        file_abs_path = str(file)
        with file.open('w', encoding='utf-8', newline='') as f:
            write = csv.writer(f)
            for log in self.logs:
                temp_list = list()
                temp_list.append(log.domain_name)
                temp_list.append(str(log.type))     # .to_string() solo se è typeRR
                temp_list.append(log.reason_phrase)
                write.writerow(temp_list)
            f.close()
            print(f".csv file '{file_abs_path}' successfully exported.")

    def write_to_txt_file(self, filename="error_logs") -> None:
        """
        Export the logs in the list to a .txt file in the output folder of the project directory. It uses the separator
        set to separate every attribute of the entry.

        Parameters
        ----------
        filename : `str`, optional
            The personalized filename without extension, default is error_logs.
        """
        file = file_utils.set_file_in_folder(Path.cwd().parent, "output", filename+".txt")
        file_abs_path = str(file)
        with open(file_abs_path, 'w') as f:       # 'w' or 'x'
            for log in self.logs:
                f.write(f"{log.domain_name}{self.separator}{str(log.type)}{self.separator}{log.reason_phrase}{self.separator}")   # .to_string() solo se è typeRR
            if len(self.logs) == 0:
                f.write("No errors occurred.")
            f.close()
            print(f".txt file '{file_abs_path}' successfully exported.")

    def merge_from(self, other: 'ErrorLogger') -> None:       # FORWARD DECLARATIONS (REFERENCES)
        """
        Method that takes another ErrorLogger object and adds (without duplicates) all the logs from the other object
        to this (self object).

        Parameters
        ----------
        other : `ErrorLogger`
            Another ErrorLogger object.
        """
        for record in other.logs:
            if record not in self.logs:
                self.logs.append(record)
