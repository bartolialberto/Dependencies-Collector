import csv
import ipaddress
import os
from pathlib import Path
from typing import List
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from utils import network_utils
from utils import file_utils


class EntryIpDatabase:
    start_range: str
    end_range: str
    as_number: str
    country_code: str
    as_description: str

    def __init__(self, entries_inline: List[str]):
        if len(entries_inline) != 5:
            raise ValueError
        else:
            self.start_range = entries_inline[0]
            self.end_range = entries_inline[1]
            self.as_number = entries_inline[2]
            self.country_code = entries_inline[3]
            self.as_description = entries_inline[4]

    def __str__(self):
        return f"{self.start_range}\t{self.end_range}\t{self.as_number}\t{self.country_code}\t{self.as_description}"


class IpDatabase:
    filepath: str
    column_separator: str
    entries: List[EntryIpDatabase]

    def __init__(self, filepath=f"input{os.sep}ip2asn-v4.tsv", column_separator='\t'):      # FileNotFoundError, '\t' = TAB
        try:
            open(filepath, "r", encoding='utf-8')
            self.filepath = filepath
            self.column_separator = column_separator
            self.entries = list()
            self.load()
        except FileNotFoundError:
            # search .tsv file in input folder
            print(f"!!! filepath='{filepath}' for ip database was not found. Attempting to find another .tsv file in input folder. !!!")
            input_folder = Path("input")
            if not input_folder.exists():
                input_folder.mkdir(parents=True, exist_ok=False)
                raise FileNotFoundError("You must create a 'input' folder in the root folder of the project and then place the .tsv ip database file in it. Visit https://iptoasn.com/ for downloads.")
            found = False
            for file in input_folder.iterdir():
                if file.is_file() and file_utils.parse_file_extension(file.name) == '.tsv':
                    with open(str(file), "r", encoding='utf-8') as f:        # FileNotFoundError
                        f.close()
                    self.filepath = str(file)
                    self.column_separator = column_separator
                    self.entries = list()
                    self.load()
                    print(f"!!! Found file '{str(file)}' for ip database. !!!")
                    found = True
            if not found:
                raise FileNotFoundError(f"!!! No .tsv file found in input folder. !!!")

    def resolve_range(self, ip_param: str or ipaddress.IPv4Address) -> EntryIpDatabase:
        ip = None
        if isinstance(ip_param, str):
            ip = ipaddress.ip_address(ip_param)
        else:
            ip = ip_param
        index = IpDatabase.binary_search(self.entries, ip)
        if index == -1:
            raise AutonomousSystemNotFoundError(ip.exploded)
        else:
            return self.entries[index]


    @staticmethod
    def binary_search(array: List[EntryIpDatabase], ip_param: ipaddress.IPv4Address) -> int:
        inf = 0
        sup = len(array) - 1
        while inf <= sup and sup - inf > 3:
            med = (inf + sup) // 2
            if ipaddress.ip_address(array[med].start_range) < ip_param:
                inf = med + 1
            elif ipaddress.ip_address(array[med].start_range) > ip_param:
                sup = med - 1
            else:
                return med
        for i in range(inf, sup):
            if network_utils.is_in_ip_range(ip_param, ipaddress.ip_address(array[i].start_range), ipaddress.ip_address(array[i].end_range)):
                return i
        return -1

    def resolve_range_OLD(self, ip_param: str or ipaddress.IPv4Address) -> EntryIpDatabase:
        ip = None
        if isinstance(ip_param, str):
            ip = ipaddress.ip_address(ip_param)
        else:
            ip = ip_param
        with open(self.filepath, "r", encoding='utf-8') as f:        # FileNotFoundError
            rd = csv.reader(f, delimiter=self.column_separator, quotechar='"')
            for row in rd:      # can we be more faster? there's an order on the file.. MergeSort???
                entry = EntryIpDatabase(row)
                start_ip_range = ipaddress.IPv4Address(entry.start_range)
                end_ip_range = ipaddress.IPv4Address(entry.end_range)
                if network_utils.is_in_ip_range(ip, start_ip_range, end_ip_range):
                    f.close()
                    return entry
            f.close()
            raise AutonomousSystemNotFoundError(ip.exploded)

    def load(self):
        with open(self.filepath, "r", encoding='utf-8') as f:        # FileNotFoundError
            rd = csv.reader(f, delimiter=self.column_separator, quotechar='"')
            for row in rd:      # can we be more faster? there's an order on the file.. MergeSort???
                entry = EntryIpDatabase(row)
                self.entries.append(entry)
            f.close()

