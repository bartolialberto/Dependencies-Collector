import csv
import os
from pathlib import Path
from entities.TypesRR import TypesRR
from utils import file_utils


class ErrorEntry:
    domain_name: str
    type: TypesRR
    reason_phrase: str

    def __init__(self, name: str, _type: TypesRR, error_message: str):
        self.domain_name = name
        self.type = _type
        self.reason_phrase = error_message


class ErrorLogger:
    logs: list

    def __init__(self):
        self.logs = list()

    def add_entry(self, entry: ErrorEntry):
        self.logs.append(entry)

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
                temp_list.append(log.name)
                temp_list.append(log.type.to_string())
                temp_list.append(log.reason_phrase)
                write.writerow(temp_list)
            f.close()

    def write_to_txt_file(self, filename="error_logs"):
        filename = file_utils.parse_filename(filename)
        output_folder = Path("output")
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=False)
        with open(f"output{os.sep}{filename}.txt", 'w') as f:       # 'w' or 'x'
            for log in self.logs:
                f.write(f"{log.name}\t{log.type.to_string()}\t{log.reason_phrase}\n")
            if len(self.logs) == 0:
                f.write("No errors occurred.")
            f.close()
