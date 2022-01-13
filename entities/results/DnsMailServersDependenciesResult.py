class DnsMailServersDependenciesResult:
    def __init__(self):
        self.mail_servers = list()

    def add_mail_server(self, mail_server: str):
        self.mail_servers.append(mail_server)
