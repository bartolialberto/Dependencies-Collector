from typing import List, Tuple
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.NoAvailablePathError import NoAvailablePathError
from utils import domain_name_utils


# TODO: docs
class DnsMailServersDependenciesResult:
    """
    This class represents the result of mail server dependencies resolving.
    It consists in a simple list of strings (mail servers).

    ...

    Attributes
    ----------
    mail_servers : List[str]
        A list of mail servers.
    """
    def __init__(self):
        """
        Initialize the object.

        """
        self.mail_servers = list()
        self.addresses = list()
        self.aliases = list()

    def add_mail_server(self, mail_server: str):
        """
        this method adds a mail server to the dependencies.


        :param mail_server: A mail server.
        :type mail_server: str
        """
        self.mail_servers.append(mail_server)

    def add_address(self, rr: RRecord):
        """
        this method adds a mail server to the dependencies.


        :param mail_server: A mail server.
        :type mail_server: str
        """
        if rr.type is not TypesRR.A:
            raise ValueError
        self.addresses.append(rr)

    def add_aliases(self, rr: RRecord):
        """
        this method adds a mail server to the dependencies.


        :param mail_server: A mail server.
        :type mail_server: str
        """
        if rr.type is not TypesRR.CNAME:
            raise ValueError
        self.aliases.append(rr)

    def resolve_mail_server(self, mail_server: str) -> Tuple[RRecord, List[RRecord]]:
        """
        This method resolves the nameserver into a valid IP address.

        :param nameserver: The name server.
        :type nameserver: str
        :raise NoAvailablePathError: If name server has no access path.
        :return: The RR of type A.
        :rtype: RRecord
        """
        try:
            path = self.__inner_resolve_mail_server(mail_server, None)
        except NoAvailablePathError:
            raise
        if len(path) == 1:
            return path[0], list()
        else:
            return path[-1], path[0:-1]

    def __inner_resolve_mail_server(self, name: str, result: List[RRecord] or None) -> List[RRecord]:
        if result is None:
            result = list()
        else:
            pass
        for rr in self.aliases:
            if domain_name_utils.equals(rr.name, name):
                result.append(rr)
                return self.__inner_resolve_mail_server(rr.get_first_value(), result)
        for rr in self.addresses:
            if domain_name_utils.equals(rr.name, name):
                result.append(rr)
                return result
        raise NoAvailablePathError(name)
