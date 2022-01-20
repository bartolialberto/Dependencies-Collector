from typing import List
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.NoAvailablePathError import NoAvailablePathError
from utils import list_utils


class Zone:
    """
    This class represent a simple zone. Semantically it represents only the data structures, not the fact
    that is a real existent zone.

    ...

    Instance Attributes
    -------------------
    name : str
        The name of the zone..
    nameservers : List[str]
        A list of all nameservers name of the zone. Some zones contain nameserver that are not directly resolvable,
        so the better solution is to keep nameservers are pure strings.
    aliases : List[RRecord]
        The aliases associated with all the nameservers of the zone.
    addresses : List[RRecord]
        The resolving RRecord associated with all the nameservers.
    """

    def __init__(self, zone_name: str, nameservers_of_zone: List[str], list_cnames: List[RRecord], addresses: List[RRecord]):
        """
        Instantiate a Zone object initializing all the attributes defined above.

        :param zone_name: The zone name.
        :type zone_name: str
        :param nameservers_of_zone: The list of all nameservers name of the zone.
        :type nameservers_of_zone: List[str]
        :param list_cnames: The list of all aliases associated with the nameservers of the zone, as RRecord of type
        CNAME (so there's the mapping between nameserver and alias).
        :type list_cnames: List[RRecord]
        :param addresses: The list of all RR of type A that resolves all nameservers.
        :type addresses: List[RRecord]
        """
        if nameservers_of_zone is None or len(nameservers_of_zone) == 0:
            self.nameservers = list()
        else:
            self.nameservers = nameservers_of_zone
        if not list_utils.are_all_objects_RRecord_and_rr_type(list_cnames, TypesRR.CNAME):
            raise ValueError()
        if nameservers_of_zone is None or len(list_cnames) == 0:
            self.aliases = list()
        else:
            self.aliases = list_cnames
        self.name = zone_name
        self.addresses = addresses

    def resolve_nameserver(self, nameserver: str) -> RRecord:
        """
        This method resolves the nameserver into a valid IP address.

        :param nameserver: The name server.
        :type nameserver: str
        :raise NoAvailablePathError: If name server has no access path.
        :return: The RR of type A.
        :rtype: RRecord
        """
        for rr in self.aliases:
            if rr.name == nameserver:
                return self.resolve_nameserver(rr.get_first_value())
        for rr in self.addresses:
            if rr.name == nameserver:
                return rr
        raise NoAvailablePathError(nameserver)

    def __str__(self) -> str:
        """
        This method returns a string representation of this object.

        :return: A string representation of this object.
        :rtype: str
        """
        return f"{self.name}, {len(self.nameservers)}#nameservers, {len(self.aliases)}#aliases, {len(self.addresses)}#addresses"

    def __eq__(self, other) -> bool:
        """
        This method returns True only if self and other are semantically equal.
        This equality depends upon the developer.

        :param other: Another Zone object.
        :type other: Zone
        :return: True or False if the 2 objects are equal.
        :rtype: bool
        """
        if isinstance(other, Zone):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return hash(repr(self))
