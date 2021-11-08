import csv
import os
from pathlib import Path
from typing import List
from entities.TypesRR import TypesRR
from utils import file_utils


class ErrorEntry:
    domain_name: str
    type: TypesRR or str
    reason_phrase: str

    def __init__(self, name: str, _type: TypesRR or str, error_message: str):
        self.domain_name = name
        self.type = _type
        self.reason_phrase = error_message


class ErrorLogger:
    logs: List[ErrorEntry]
    separator: str

    def __init__(self, separator="\t"):
        self.logs = list()
        self.separator = separator

    def add_entry(self, entry: ErrorEntry):
        self.logs.append(entry)

    def set_separator(self, separator: str):
        self.separator = separator

    def write_to_csv_file(self, filename="error_logs"):
        filename = file_utils.parse_filename(filename)
        output_folder = Path("output")
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=False)
        csv_file = Path(f"output{os.sep}{filename}.csv")
        with csv_file.open('w', encoding='utf-8', newline='') as f:
            write = csv.writer(f)
            for log in self.logs:
                temp_list = []
                temp_list.append(log.domain_name)
                temp_list.append(str(log.type))     # .to_string() solo se è typeRR
                temp_list.append(log.reason_phrase)
                write.writerow(temp_list)
            f.close()
            print(f".csv file '{os.sep}output{os.sep}{csv_file.name}' successfully exported.")

    def write_to_txt_file(self, filename="error_logs"):
        filename = file_utils.parse_filename(filename)
        output_folder = Path("output")
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=False)
        txt_filename = f"output{os.sep}{filename}.txt"
        with open(txt_filename, 'w') as f:       # 'w' or 'x'
            for log in self.logs:
                f.write(f"{log.domain_name}{self.separator}{str(log.type)}{self.separator}{log.reason_phrase}{self.separator}")   # .to_string() solo se è typeRR
            if len(self.logs) == 0:
                f.write("No errors occurred.")
            f.close()
            print(f".txt file '{txt_filename}' successfully exported.")

    def merge_from(self, other: 'ErrorLogger'):       # FORWARD DECLARATIONS (REFERENCES)
        for record in other.logs:
            if record not in self.logs:
                self.logs.append(record)
