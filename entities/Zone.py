import copy
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
        The name of the zone.
    nameservers : List[str]
        A list of all nameservers name of the zone. Some zones contain nameserver that are not directly resolvable,
        so the better solution is to keep nameservers are pure strings.
    aliases : List[RRecord]
        The aliases associated with all the nameservers of the zone.
    zone_aliases : List[RRecord]
        The aliases associated with the zone name.
    addresses : List[RRecord]
        The resolving RRecord associated with all the nameservers.
    """

    def __init__(self, zone_name: str, nameservers_of_zone: List[str], name_servers_cnames: List[RRecord], addresses: List[RRecord], zone_name_cnames: List[RRecord]):
        """
        Instantiate a Zone object initializing all the attributes defined above.

        :param zone_name: The zone name.
        :type zone_name: str
        :param nameservers_of_zone: The list of all nameservers name of the zone.
        :type nameservers_of_zone: List[str]
        :param name_servers_cnames: The list of all aliases associated with the nameservers of the zone, as RRecord of type
        CNAME (so there's the mapping between nameserver and alias).
        :type name_servers_cnames: List[RRecord]
        :param addresses: The list of all RR of type A that resolves all nameservers.
        :type addresses: List[RRecord]
        """
        if nameservers_of_zone is None or len(nameservers_of_zone) == 0:
            self.nameservers = list()
        else:
            self.nameservers = nameservers_of_zone
        if not list_utils.are_all_objects_RRecord_of_type(name_servers_cnames, TypesRR.CNAME):
            raise ValueError()
        if nameservers_of_zone is None or len(name_servers_cnames) == 0:
            self.aliases = list()
        else:
            self.aliases = name_servers_cnames
        if not list_utils.are_all_objects_RRecord_of_type(zone_name_cnames, TypesRR.CNAME):
            raise ValueError()
        else:
            self.zone_aliases = zone_name_cnames        # c'è dipendenza da dove la troviamo
        self.name = zone_name
        self.addresses = addresses
        if len(self.nameservers) != len(self.addresses):
            raise ValueError

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

    def stamp_access_path(self, name_server: str) -> str:
        """
        This method return a string that represents schematically the access path and the name server parameter.

        :param name_server: A name server of the self zone object.
        :type name_server: str
        :return: The string representation.
        :rtype: str
        """
        if name_server not in self.nameservers:
            raise ValueError
        try:
            return self.__inner_stamp_access_path(name_server, '')
        except NoAvailablePathError:
            raise

    def __inner_stamp_access_path(self, name: str, result: str) -> str:
        """
        Recursive auxiliary method used by the 'stamp_access_path' method.

        :param name: A domain name of the self zone object.
        :type name: str
        :param result: The result of the method carried through each recursive execution.
        :type result: str
        :return: The string representation.
        :rtype: str
        """
        result = result + name
        for rr in self.aliases:
            if domain_name_utils.equals(rr.name, name):
                result = result + " ---> "
                return self.__inner_stamp_access_path(rr.get_first_value(), result)
        for rr in self.addresses:
            if domain_name_utils.equals(rr.name, name):
                result = result + " ===> " + str(rr.values)
                return result
        raise NoAvailablePathError(name)

    def resolve_zone_name_resolution_path(self) -> List[RRecord]:
        # no aliases ==> NoAvailablePathError
        inner_result = self.__inner_reversed_resolve_zone_name_resolution_path(self.name, None)
        if len(inner_result) == 0:
            raise NoAvailablePathError(self.name)
        return list(reversed(inner_result))

    def __inner_reversed_resolve_zone_name_resolution_path(self, name: str, result: List[RRecord] or None) -> List[RRecord]:
        # no aliases ==> empty list
        if result is None:
            result = list()
        else:
            pass
        for rr in self.zone_aliases:
            if domain_name_utils.equals(rr.get_first_value(), name):
                result.append(rr)
                return self.__inner_reversed_resolve_zone_name_resolution_path(rr.name, result)
        return result

    def stamp_zone_name_resolution_path(self) -> str:
        """
        This method return a string that represents schematically the name resolution path of the (self) zone name.

        :return: The string representation.
        :rtype: str
        """
        try:
            result = self.resolve_zone_name_resolution_path()
        except NoAvailablePathError:
            return f"{self.name}"
        string = copy.deepcopy(result[0].name)
        for rr in result:
            string = string + ' ---> ' + rr.get_first_value()
        return string

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
