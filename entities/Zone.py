from typing import List
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.NoAvailablePathError import NoAvailablePathError
from utils import list_utils, domain_name_utils


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

    def resolve_name_server_access_path(self, nameserver: str) -> RRecord:
        """
        This method resolves the nameserver into a valid IP address.

        :param nameserver: The name server.
        :type nameserver: str
        :raise NoAvailablePathError: If name server has no access path.
        :return: The RR of type A.
        :rtype: RRecord
        """
        for rr in self.aliases:
            if domain_name_utils.equals(rr.name, nameserver):
                return self.resolve_name_server_access_path(rr.get_first_value())
        for rr in self.addresses:
            if domain_name_utils.equals(rr.name, nameserver):
                return rr
        raise NoAvailablePathError(nameserver)

    def is_ip_of_name_servers(self, ip_address: str) -> str:
        """
        This method resolves a string IP address into a name server of the zone if there's correspondence.

        :param ip_address: An IP address.
        :type ip_address: str
        :raise ValueError: If there's no correspondence.
        :return: The name server.
        :rtype: str
        """
        for rr in self.addresses:
            if ip_address in rr.values:
                canonical_name = rr.name
                return self.__resolve_name_server_from_ip_address(canonical_name)
        raise ValueError

    def __resolve_name_server_from_ip_address(self, canonical_name: str) -> str:
        """
        This method is an auxiliary recursive method that helps the 'is_ip_of_name_servers' method of this class.

        :param canonical_name: The canonical name.
        :type canonical_name: str
        :raise ValueError: If there's no correspondence.
        :return: The name server.
        :rtype: str
        """
        for rr in self.aliases:
            if domain_name_utils.equals(rr.get_first_value(), canonical_name):
                return self.__resolve_name_server_from_ip_address(rr.name)
        for name_server in self.nameservers:
            if domain_name_utils.equals(canonical_name, name_server):
                return name_server
        raise ValueError

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
            return domain_name_utils.equals(self.name, other.name)
        else:
            return False

    def __hash__(self):
        return hash(repr(self))
