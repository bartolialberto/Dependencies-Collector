from ipaddress import IPv4Address
from typing import List, Tuple
from entities.DomainName import DomainName
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from entities.paths.APath import APath
from entities.paths.MXPath import MXPath
from exceptions.DomainNameNotInPathError import DomainNameNotInPathError
from exceptions.NoAvailablePathError import NoAvailablePathError
from utils import domain_name_utils


# TODO: docs
class MailDomainResolvingResult:
    """
    This class represents the result of mail server dependencies resolving.
    It consists in a simple list of strings (mail servers).

    ...

    Attributes
    ----------
    mail_servers : List[str]
        A list of mail servers.
    """
    def __init__(self, mx_path: MXPath):
        """
        Initialize the object.

        """
        self.mail_domain_path = mx_path
        self.mail_servers_paths = dict()
        if mx_path.get_resolution().type == TypesRR.MX:
            for value in mx_path.get_resolution().values:
                if isinstance(value, DomainName):
                    self.mail_servers_paths[value] = None
                elif isinstance(value, IPv4Address):
                    # self.mail_servers_paths[value] = None
                    pass
                else:
                    raise ValueError
        else:
            raise ValueError

    def add_mail_server_access(self, a_path: APath):
        """
        this method adds a mail server to the dependencies.


        :param mail_server: A mail server.
        :type mail_server: str
        """
        try:
            self.mail_servers_paths[a_path.get_qname()] = a_path
        except KeyError:
            raise

    def add_unresolved_mail_server_access(self, mail_server: DomainName) -> None:
        self.mail_servers_paths[mail_server] = None

    def __eq__(self, other) -> bool:
        return self.mail_domain_path == other.mail_domain_path and self.mail_servers_paths == other.mail_servers_paths

    def __iter__(self):
        return self.mail_servers_paths.__iter__()

    def __next__(self):
        return self.mail_servers_paths.__iter__().__next__()

    def __hash__(self):
        return hash(repr(self))
