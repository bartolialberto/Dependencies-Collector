from entities.error_log.ErrorLog import ErrorLog
from entities.results.DnsMailServersDependenciesResult import DnsMailServersDependenciesResult


class MultipleDnsMailServerDependenciesResult:
    def __init__(self):
        self.dependencies = dict()
        self.error_logs = list()

    def add_dependency(self, mail_domain: str, mail_servers_dependency: DnsMailServersDependenciesResult):
        self.dependencies[mail_domain] = mail_servers_dependency

    def append_error_log(self, log: ErrorLog):
        self.error_logs.append(log)
