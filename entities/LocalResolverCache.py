import csv
import Zones
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from exceptions.NoRecordInCacheError import NoRecordInCacheError


class LocalResolverCache:
    cache: list

    def __init__(self):
        self.cache = list()

    def add_entry(self, entry: Zones.RRecord):
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

    def write_to_file(self):
        fhand = open(csv, "w")
        line = ""
        for rr in self.cache:
            line = rr.name + "," + rr.type
            if rr.values == "NoAnswer":
                line = line + ",NoAnswer"
            elif rr.values == "NXDomain":
                line = line + ",NXDomain"
            else:
                for value in rr.values:
                    line = line + "," + value
            line = line + "\n"
            fhand.write(line)
        fhand.close()

    # TODO
    def load(self, csv):
        fhand = open(csv, "r")
        for line in fhand:
            splitted = line.split("\t")     # \t is TAB
            if len(splitted) >= 3:
                if splitted[2].strip() == "NoAnswer" or splitted[2].strip() == "NXDomain":
                    self.cache.append(RRecord(splitted[0], splitted[1], splitted[2].strip()))
                    continue
                list_respose = list()
                for a in splitted[2:]:
                    list_respose.append(a.strip())
                rrecord = RRecord(splitted[0], splitted[1], list_respose)
                self.cache.append(rrecord)
            else:
                print("Line: ", line, " has too few arguments")
        fhand.close()

    # TODO
    def write_to_file(self):
        fhand = open(csv, "w")
        line = ""
        for rr in self.cache:
            line = rr.name + "," + rr.type
            if rr.values == "NoAnswer":
                line = line + ",NoAnswer"
            elif rr.values == "NXDomain":
                line = line + ",NXDomain"
            else:
                for value in rr.values:
                    line = line + "," + value
            line = line + "\n"
            fhand.write(line)
        fhand.close()
