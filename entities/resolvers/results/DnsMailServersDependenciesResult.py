from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR


# TODO: docs
from exceptions.NoAvailablePathError import NoAvailablePathError
from utils import domain_name_utils


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

    def resolve_mail_server(self, mail_server: str) -> RRecord:
        """
        This method resolves the nameserver into a valid IP address.

        :param nameserver: The name server.
        :type nameserver: str
        :raise NoAvailablePathError: If name server has no access path.
        :return: The RR of type A.
        :rtype: RRecord
        """
        for rr in self.aliases:
            if domain_name_utils.equals(rr.name, mail_server):
                return self.resolve_mail_server(rr.get_first_value())
        for rr in self.addresses:
            if domain_name_utils.equals(rr.name, mail_server):
                return rr
        raise NoAvailablePathError(mail_server)
