import copy
from ipaddress import IPv4Address
from typing import List, Set

from entities.paths.APath import APath
from entities.DomainName import DomainName
from entities.paths.NSPath import NSPath
from entities.RRecord import RRecord
from exceptions.DomainNameNotInPathError import DomainNameNotInPathError
from exceptions.NoAvailablePathError import NoAvailablePathError


class Zone:
    """
    This class represent a simple zone. Semantically it represents only the data structures, not the fact
    that is a real existent zone.

    ...

    Instance Attributes
    -------------------
    name : str
        The name of the zone.
    nameservers : List[DomainName]
        A list of all nameservers name of the zone. Some zones contain nameserver that are not directly resolvable,
        so the better solution is to keep nameservers are pure strings.
    aliases : List[RRecord]
        The aliases associated with all the nameservers of the zone.
    zone_aliases : List[RRecord]
        The CNAME RRs that leads to the zone name if encountered.
    addresses : List[RRecord]
        The resolving RRecord associated with all the nameservers.
    """

    def __init__(self, name_path: NSPath, nameservers_path: List[APath]):
        """
        Instantiate a Zone object initializing all the attributes defined above.

        :param zone_name: The zone name.
        :type zone_name: DomainName
        :param nameservers_of_zone: The list of all nameservers name of the zone.
        :type nameservers_of_zone: List[DomainName]
        :param name_servers_cnames: The list of all aliases associated with the nameservers of the zone, as RRecord of type
        CNAME (so there's the mapping between nameserver and alias).
        :type name_servers_cnames: List[RRecord]
        :param addresses: The list of all RR of type A that resolves all nameservers.
        :type addresses: List[RRecord]
        """
        self.name_path = name_path
        self.name = name_path.get_canonical_name()
        self.name_servers = nameservers_path

    def nameservers(self, as_strings=False) -> List[str] or List[DomainName]:
        name_servers = list(map(lambda a_path: a_path.get_qname(), self.name_servers))
        if as_strings:
            return list(map(lambda ns: ns._second_component_, name_servers))
        else:
            return name_servers

    def resolve_name_server_access_path(self, nameserver: DomainName) -> RRecord:
        """
        This method resolves the nameserver into a valid IP address.

        :param nameserver: The name server.
        :type nameserver: str
        :raise NoAvailablePathError: If name server has no access path.
        :return: The RR of type A.
        :rtype: RRecord
        """
        for name_server_ap in self.name_servers:
            try:
                return name_server_ap.resolve(nameserver)
            except DomainNameNotInPathError:
                pass
        raise NoAvailablePathError(nameserver.string)

    def is_ip_of_name_servers(self, ip_address: IPv4Address, return_canonical_name=False) -> DomainName:
        """
        This method resolves an IP address into a name server of the zone if there's correspondence.

        :param ip_address: An IP address.
        :type ip_address: ipaddress.IPv4Address
        :raise ValueError: If there's no correspondence.
        :return: The name server.
        :rtype: DomainName
        """
        for ap in self.name_servers:
            rr = ap.get_resolution()
            if ip_address in rr.values:
                if return_canonical_name:
                    return ap.get_canonical_name()
                else:
                    return ap.get_qname()
        raise ValueError

    def parse_every_domain_name(self, with_zone_name=False, root_included=False, tld_included=False) -> Set[DomainName]:
        result = set()
        for rr in self.name_path:
            for name in rr.name.parse_subdomains(root_included=root_included, self_included=True):
                result.add(name)
        for a_path in self.name_servers:
            for rr in a_path:
                for name in rr.name.parse_subdomains(root_included=root_included, self_included=True):
                    result.add(name)
        if not with_zone_name:
            result.remove(self.name)
        if not root_included:
            try:
                result.remove(DomainName('.'))
            except KeyError:
                pass
        if not tld_included:
            new_result = copy.deepcopy(result)
            for domain_name in result:
                if domain_name.is_tld():
                    pass
                else:
                    new_result.add(domain_name)
            result = new_result
        return result


    def __str__(self) -> str:
        """
        This method returns a string representation of this object.

        :return: A string representation of this object.
        :rtype: str
        """
        return f"{self.name}\t{len(self.name_servers)}#nameservers"

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

    def __hash__(self) -> int:
        return hash(self.name)
