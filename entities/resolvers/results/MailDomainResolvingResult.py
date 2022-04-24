from ipaddress import IPv4Address
from typing import Iterator
from entities.DomainName import DomainName
from entities.enums.TypesRR import TypesRR
from entities.paths.APath import APath
from entities.paths.MXPath import MXPath


class MailDomainResolvingResult:
    """
    This class represents the result of mail server dependencies resolving.
    It consists in the path retrieved from a MX query of the mail domain and a dictionary for each mail server (as key)
    that takes an APath object as value.

    ...

    Attributes
    ----------
    mail_domain_path : MXPath
        A list of mail servers.
    mail_servers_paths : Dict[DomainName, Optional[APath]
        A list of mail servers.
    """
    def __init__(self, mx_path: MXPath):
        """
        Initialize the object. In particular sets every value of the mail_servers_paths to None, only later with the
        add_mail_server_access method it can be set the APath for a mail server.

        :raise ValueError: If an unexpected value type is encountered in the MXPath parameter or if the MXPath parameter
        is not a MXPath object.
        """
        self.mail_domain_path = mx_path
        self.mail_servers_paths = dict()
        if mx_path.get_resolution().type == TypesRR.MX:
            for value in mx_path.get_resolution().values:
                if isinstance(value, DomainName):
                    self.mail_servers_paths[value] = None
                elif isinstance(value, IPv4Address):
                    # TODO: NOT HANDLED:
                    pass
                else:
                    raise ValueError
        else:
            raise ValueError

    def add_mail_server_access(self, a_path: APath):
        """
        This method adds a mail server APath to the dependencies.


        :param a_path: An APath object.
        :type a_path: APath
        :raise KeyError: If the APath doesn't reference a mail server related to the mail domain.
        """
        try:
            self.mail_servers_paths[a_path.get_qname()] = a_path
        except KeyError:
            raise

    def __eq__(self, other) -> bool:
        """
        This method returns a boolean for comparing 2 objects equality.

        :param other:
        :return: The result of the comparison.
        :rtype: bool
        """
        if isinstance(other, MailDomainResolvingResult):
            return self.mail_domain_path == other.mail_domain_path and self.mail_servers_paths == other.mail_servers_paths
        else:
            return False

    def __iter__(self) -> Iterator[DomainName]:
        """
        Class is iterable through the mail servers dictionary (the keys).

        :return: The iterator.
        :rtype: Iterator[DomainName]
        """
        return self.mail_servers_paths.__iter__()

    def __next__(self) -> DomainName:
        """
        Class is iterable through the mail servers dictionary (the keys).

        :return: The next domain name.
        :rtype: DomainName
        """
        return self.mail_servers_paths.__iter__().__next__()

    def __hash__(self):
        """
        This method returns the hash of this object. Should be defined alongside the __eq__ method with the same
        returning value from 2 objects.

        :return: Hash of this object.
        :rtype: int
        """
        return hash(repr(self))
