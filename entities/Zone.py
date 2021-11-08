from entities.TypesRR import TypesRR
from utils import list_utils


class Zone:
    name: str
    zone_nameservers: list
    cnames: list

    def __init__(self, zone_name: str, list_rr_a_of_nsz: list, list_cnames: list):
        if not list_utils.are_all_objects_RRecord_and_rr_type(list_rr_a_of_nsz, TypesRR.A):
            raise ValueError()
        if list_rr_a_of_nsz is None or len(list_rr_a_of_nsz) == 0:
            self.zone_nameservers = list()
        else:
            self.zone_nameservers = list_rr_a_of_nsz
        if not list_utils.are_all_objects_RRecord_and_rr_type(list_cnames, TypesRR.CNAME):
            raise ValueError()
        if list_rr_a_of_nsz is None or len(list_cnames) == 0:
            self.cnames = list()
        else:
            self.cnames = list_cnames
        self.name = zone_name

