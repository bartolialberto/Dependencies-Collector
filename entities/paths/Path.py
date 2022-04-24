import abc
from exceptions.DomainNameNotInPathError import DomainNameNotInPathError
from utils import resource_records_utils
from abc import ABC
from typing import List, Union, Iterator
from entities.DomainName import DomainName
from entities.RRecord import RRecord


class Path(ABC):
    """
    This class represents a list of resource records traversed to get the resource record wanted. In particular the list
    of resource records it is formed firstly by a chain of CNAME resource records (or none of it) and then a final
    resource record corresponding on the DNS query executed.
    Example: A type query for name: www.youtube.com

        www.youtube.com. --CNAME-> youtube-ui.l.google.com. ==A=> [142.250.180.174, .. ]

    This class is an abstract data structure for this chain of resource records, that doesn't take in account the final
    'resolution' resource record.

    ...

    Attributes
    ----------
    path : List[RRecord]
        Abstract property. List of resource records.
    """
    @property
    @abc.abstractmethod
    def path(self) -> List[RRecord]:
        raise NotImplementedError

    @path.setter
    @abc.abstractmethod
    def path(self, new_val: List[RRecord]) -> List[RRecord]:
        raise NotImplementedError

    def get_resolution(self) -> RRecord:
        """
        It returns the final resource record that 'resolve' the chain.

        :return: The final resource record.
        :rtype: RRecord
        """
        return self.path[-1]

    def get_cname_chain(self, as_resource_records=True) -> Union[List[RRecord], List[DomainName]]:
        """
        It returns the CNAME resource records chain before the final 'resolving' resource record. The chain can be
        returned as a list of RRecord objects or as a list of DomainName objects (more straight-forward in some
        cases), depending on the as_resource_records parameter.

        :param as_resource_records: Parameter to set if the result should be resource records or domain names.
        :type as_resource_records: bool
        :return: The CNAME resource records chain.
        :rtype: Union[List[RRecord], List[DomainName]]
        """
        if as_resource_records:
            return self.path[0:-1]
        else:
            result = list()
            result.append(self.path[0].name)
            for rr in self.path[0:-1]:
                result.append(rr.get_first_value())
            return result

    def get_canonical_name(self) -> DomainName:
        """
        Returns the canonical name of the path, which means the final domain name that yields to a resource record of
        the wanted type.

        :return: The canonical name of the path.
        :rtype: DomainName
        """
        return self.get_resolution().name

    def get_qname(self) -> DomainName:
        """
        Returns the query name of the path, which means the domain name used to execute the DNS query that produces the
        self Path object.

        :return: The query name of the path.
        :rtype: DomainName
        """
        return self.path[0].name

    def resolve(self, domain_name: DomainName) -> RRecord:
        """
        Given any domain name as parameter, this method returns the resolution resource record if the parameter it's
        part (as name or value) of any of the resource records of the path.

        :param domain_name: A domain name
        :type domain_name: DomainName
        :raise DomainNameNotInPathError: If the domain name parameter is not part (as name or value) of any resource
        record of the path.
        :return: The resolution record
        :rtype: RRecord
        """
        for rr in self.path:
            if rr.name == domain_name:
                return self.get_resolution()
        if self.get_resolution().name == domain_name:
            return self.get_resolution()
        raise DomainNameNotInPathError(domain_name)

    def stamp(self) -> str:
        """
        Returns a nice and schematic representation of the self object.

        :return: The self object representation.
        :rtype: str
        """
        result = ''
        if len(self.get_cname_chain()) == 0:
            result = result + str(self.get_resolution().name)
        else:
            for i, rr in enumerate(self.get_cname_chain()):
                if i == 0:
                    result = str(rr.name) + " --CNAME-> " + rr.get_first_value().string
                else:
                    result = result + " --CNAME-> " + rr.get_first_value().string
        if len(self.get_cname_chain()) == 0:
            return self.get_resolution().name.string + " =="+self.get_resolution().type.to_string()+"=> " + resource_records_utils.stamp_values(self.get_resolution().type, self.get_resolution().values)
        else:
            return result + " =="+self.get_resolution().type.to_string()+"=> " + resource_records_utils.stamp_values(self.get_resolution().type, self.get_resolution().values)

    def __str__(self) -> str:
        """
        This method returns a human-readable string representation of this object.

        :return: A human-readable string representation of this object.
        :rtype: str
        """
        return self.stamp()

    def __eq__(self, other) -> bool:
        """
        This method returns a boolean for comparing 2 objects equality.

        :param other:
        :return: The result of the comparison.
        :rtype: bool
        """
        if isinstance(other, Path):
            return self.get_resolution() == other.get_resolution() and self.get_qname() == other.get_qname()
        else:
            return False

    def __hash__(self) -> int:
        """
        This method returns the hash of this object. Should be defined alongside the __eq__ method with the same
        returning value from 2 objects.

        :return: Hash of this object.
        :rtype: int
        """
        return hash((self.get_resolution(), self.get_qname()))

    def __iter__(self) -> Iterator[RRecord]:
        """
        Class is iterable through the path (being a list then provides order when iterating).

        :return: The iterator.
        :rtype: Iterator[RRecord]
        """
        return self.path.__iter__()

    def __next__(self) -> RRecord:
        """
        Class is iterable through the path (being a list then provides order when iterating).

        :return: The next RRecord
        :rtype: RRecord
        """
        return self.path.__iter__().__next__()

    @staticmethod
    def check_path_integrity(path: List[RRecord]) -> bool:
        """
        Static methods that checks the integrity and consistency of a list of resource records forming a Path object.
        The properties to check are:
            - given a rr: A CNAME B, the next one must provide B as the name value
            - every resource record of the CNAME chain must be a CNAME resource record

        :param path:
        :return:
        """
        if len(path) == 0:
            return False
        elif len(path) == 1:
            return True
        else:
            prev_alias = path[0].get_first_value()
            for rr in path[1:]:
                if rr.name != prev_alias:
                    return False
                prev_alias = rr.get_first_value()
            return True
