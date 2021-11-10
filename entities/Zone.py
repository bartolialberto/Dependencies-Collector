from typing import List
from entities.TypesRR import TypesRR
from utils import list_utils


class Zone:
    """
    This class represent a simple zone. Semantically it represents only the data structures, not the fact
    that is a real existent zone.

    ...

    Attributes
    ----------
    name : `str`
        The name of the zone..
    zone_nameservers : `list[str]`
        A list of all nameservers name of the zone.
    cnames : `list[str]`
        The aliases associated with all the nameservers of the zone.
    """
    name: str
    zone_nameservers: List[str]
    cnames: List[str]

    def __init__(self, zone_name: str, list_rr_a_of_nsz: List[str], list_cnames: List[str]):
        """
        Instantiate a Zone object initializing all the attributes defined above.

        Parameters
        ----------
        zone_name : `str`
            The zone name.
        list_rr_a_of_nsz : `list[str]`
            The list of all nameservers name of the zone.
        list_cnames : `str` of 'list[str]`
            The list of aliases associated with all the nameservers of the zone.
        """
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

