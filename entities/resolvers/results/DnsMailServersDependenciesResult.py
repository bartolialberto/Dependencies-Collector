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

    def add_mail_server(self, mail_server: str):
        """
        this method adds a mail server to the dependencies.


        :param mail_server: A mail server.
        :type mail_server: str
        """
        self.mail_servers.append(mail_server)
