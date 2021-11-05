import csv
import Zones
from entities.TypesRR import TypesRR
from exceptions.NoRecordInCacheError import NoRecordInCacheError


class LocalResolverCache:
    cache: list

    def __init__(self):
        self.cache = list()

    def add_entry(self, entry: Zones.RRecord):
        self.cache.append(entry)

    def look_up_first(self, domain_name: str, _type: TypesRR):
        for rr in self.cache:
            if rr.name == domain_name and rr.type == _type.value:
                return rr
        raise NoRecordInCacheError(domain_name, _type)

    def look_up(self, domain_name: str, _type: TypesRR):
        result = []
        for rr in self.cache:
            if rr.name == domain_name and rr.type == _type.value:
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
