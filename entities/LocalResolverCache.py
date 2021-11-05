import csv
import os
from pathlib import Path

from exceptions.NotResourceRecordTypeError import NotResourceRecordTypeError
from utils import file_utils
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from exceptions.NoRecordInCacheError import NoRecordInCacheError


class LocalResolverCache:
    cache: list

    def __init__(self):
        self.cache = list()

    def add_entry(self, entry: RRecord):
        self.cache.append(entry)

    def look_up_first(self, domain_name: str, _type: TypesRR) -> RRecord:
        for rr in self.cache:
            if rr.name == domain_name and rr.type == _type.to_string():
                return rr
        raise NoRecordInCacheError(domain_name, _type)

    def look_up(self, domain_name: str, _type: TypesRR) -> list:
        result = []
        for rr in self.cache:
            if rr.name == domain_name and rr.type == _type.to_string():
                result.append(rr)
        if len(result) == 0:
            raise NoRecordInCacheError(domain_name, _type)
        else:
            return result

    def load_csv(self, path: str):
        fhand = open(path, "r")
        for line in fhand:
            row = line.replace("[", "")
            row = row.replace("]", "")
            row = row.replace('"', "")
            row = row.replace("\n", "")
            split_row = row.split(",")

            try:
                _type = TypesRR.parse_from_string(split_row[1])
            except NotResourceRecordTypeError:
                continue

            # parsing values
            values = []
            for val in split_row[2:]:
                values.append(val)

            self.cache.append(RRecord(split_row[0], _type, values))
        fhand.close()

    def write_to_csv_file(self, filename="cache"):
        filename = file_utils.parse_filename(filename)
        output_folder = Path("output")
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=False)
        csv_file = Path(f"output{os.sep}{filename}.csv")
        with csv_file.open('w', encoding='utf-8', newline='') as f:
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
                temp_list.append(tmp)
                write.writerow(temp_list)
            f.close()

    def write_to_txt_file(self, filename="cache"):
        filename = file_utils.parse_filename(filename)
        output_folder = Path("output")
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=False)
        with open(f"output{os.sep}{filename}.txt", 'w') as f:       # 'w' or 'x'
            for rr in self.cache:
                temp = f"{rr.name}\t{rr.type.to_string()}\t["
                for index, val in enumerate(rr.values):
                    temp += val
                    if not index == len(rr.values) - 1:
                        temp += " "
                temp += "]\n"
                f.write(temp)
            f.close()
