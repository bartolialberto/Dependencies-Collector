from typing import List
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from utils import list_utils


class Zone:
    """
    This class represent a simple zone. Semantically it represents only the data structures, not the fact
    that is a real existent zone.

    ...

    Instance Attributes
    -------------------
    name : `str`
        The name of the zone..
    nameservers : `List[RRecord]`
        A list of all nameservers name of the zone.
    cnames : `list[str]`
        The aliases associated with all the nameservers of the zone.
    """

    def __init__(self, zone_name: str, list_rr_a_of_nsz: List[RRecord], list_cnames: List[str]):
        """
        Instantiate a Zone object initializing all the attributes defined above.

        :param zone_name: The zone name.
        :type zone_name: str
        :param list_rr_a_of_nsz: The list of all nameservers name of the zone, as RRecord of type A (so there's the
        mapping between domain name and ip address.
        :type list_rr_a_of_nsz: List[RRecord]
        :param list_cnames: The list of aliases associated with all the nameservers of the zone.
        :type list_cnames: List[str]
        """
        if not list_utils.are_all_objects_RRecord_and_rr_type(list_rr_a_of_nsz, TypesRR.A):
            raise ValueError()
        if list_rr_a_of_nsz is None or len(list_rr_a_of_nsz) == 0:
            self.nameservers = list()
        else:
            self.nameservers = list_rr_a_of_nsz
        if not list_utils.are_all_objects_RRecord_and_rr_type(list_cnames, TypesRR.CNAME):
            raise ValueError()
        if list_rr_a_of_nsz is None or len(list_cnames) == 0:
            self.cnames = list()
        else:
            self.cnames = list_cnames
        self.name = zone_name
