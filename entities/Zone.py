import copy
from typing import List, Set, Union, Dict
from entities.paths.APath import APath
from entities.DomainName import DomainName
from entities.paths.NSPath import NSPath
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.UnknownReasonError import UnknownReasonError


class Zone:
    """
    This class represent a simplified DNS zone. Semantically it represents only the data structures, not the fact
    that is a real existent zone.

    ...

    Instance Attributes
    -------------------
    name_path : NSPath
        NSPath executed for the zone name.
    name : DomainName
        Zone name.
    name_servers : List[APath]
        List of APath associated to each mail server (so each DNS query of type A had a valid result).
    unresolved_name_servers : Dict[DomainName, Union[DomainNonExistentError, NoAnswerError, UnknownReasonError]]
        Dictionary of mail servers that associates each mail server domain name and the corresponding exception raised.
    """

    def __init__(self, name_path: NSPath, nameservers_path: List[APath], unresolved_nameservers_path: Dict[DomainName, Union[DomainNonExistentError, NoAnswerError, UnknownReasonError]]):
        """
        Instantiate the object.

        :param name_path: NSPath executed for the zone name.
        :type name_path: NSPath
        :param nameservers_path: List of APath associated to each mail server (so each DNS query of type A had a valid
        result).
        :type nameservers_path: List[APath]
        :param unresolved_nameservers_path: Dictionary of mail servers that associates each mail server domain name and
        the corresponding exception raised.
        :type unresolved_nameservers_path: Dict[DomainName, Union[DomainNonExistentError, NoAnswerError, UnknownReasonError]]
        """
        if len(name_path.get_resolution().values) != (len(nameservers_path) + len(unresolved_nameservers_path.keys())):
            raise ValueError
        self.name_path = name_path
        self.name = name_path.get_canonical_name()
        self.name_servers = nameservers_path
        self.unresolved_name_servers = unresolved_nameservers_path

    def nameservers(self, as_strings=False) -> Union[List[str], List[DomainName]]:
        """
        Returns nameservers of the zone.

        :param as_strings: Flag that sets if the returning list contains strings or DomainName objects.
        :type as_strings: bool
        :return: List of nameservers.
        :rtype: Union[List[str], List[DomainName]]
        """
        name_servers = list(map(lambda a_path: a_path.get_qname(), self.name_servers))
        for ns in self.unresolved_name_servers.keys():
            name_servers.append(ns)
        if as_strings:
            return list(map(lambda ns: ns._second_component_, name_servers))
        else:
            return name_servers

    def parse_every_domain_name(self, with_zone_name=False, root_included=False, tld_included=False) -> Set[DomainName]:
        """
        This methods returns every domain and sub-domain regarding the zone. It considers names from zone name, every
        nameserver, every CNAME and computes all subdomains of such names.

        :param with_zone_name: Flag that sets if zone name should be considered.
        :type with_zone_name: bool
        :param root_included: Flag that sets if root zone should be considered.
        :type root_included: bool
        :param tld_included: Flag that sets if TLDs should be considered.
        :type tld_included: bool
        :return: All domains related to the zone.
        :rtype: Set[DomainName]
        """
        result = set()
        for rr in self.name_path:
            for name in rr.name.parse_subdomains(root_included, tld_included, True):
                result.add(name)
        for a_path in self.name_servers:
            for rr in a_path:
                for name in rr.name.parse_subdomains(root_included, tld_included, True):
                    result.add(name)
        for unresolved_name_server in self.unresolved_name_servers.keys():
            for name in unresolved_name_server.parse_subdomains(root_included, tld_included, True):
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
        This method returns a human-readable string representation of this object.

        :return: A human-readable string representation of this object.
        :rtype: str
        """
        return f"{self.name}\t{len(self.name_servers)+len(self.unresolved_name_servers.keys())}#nameservers"

    def __eq__(self, other) -> bool:
        """
        This method returns a boolean for comparing 2 objects equality.

        :param other:
        :return: The result of the comparison.
        :rtype: bool
        """
        if isinstance(other, Zone):
            return self.name == other.name
        else:
            return False

    def __hash__(self) -> int:
        """
        This method returns the hash of this object. Should be defined alongside the __eq__ method with the same
        returning value from 2 objects.

        :return: Hash of this object.
        :rtype: int
        """
        return hash(self.name)
