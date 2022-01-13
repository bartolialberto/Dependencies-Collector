import ipaddress
from entities.resolvers.IpAsDatabase import EntryIpAsDatabase
from entities.results.AutonomousSystemResolutionResults import AutonomousSystemResolutionResults, \
    AutonomousSystemResolutionValues
from entities.scrapers.ROVPageScraper import RowPrefixesTable


class ASResolverValueForROVPageScraping:
    def __init__(self, ip_address: ipaddress.IPv4Address or None, entry__as_database: EntryIpAsDatabase, network: ipaddress.IPv4Network or None):
        self.ip_address = ip_address
        self.entry_as_database = entry__as_database
        self.entry_rov_page = None
        self.belonging_network = network

    def insert_rov_entry(self, entry: RowPrefixesTable or None):
        self.entry_rov_page = entry

    @staticmethod
    def construct_from(value: AutonomousSystemResolutionValues):
        return ASResolverValueForROVPageScraping(value.ip_address, value.entry, value.belonging_network)


class ASResolverResultForROVPageScraping:
    def __init__(self, as_results: AutonomousSystemResolutionResults):
        self.results = dict()
        for name_server in as_results.results.keys():
            if as_results.results[name_server].entry.as_number is None:
                continue
            try:
                self.results[as_results.results[name_server].entry.as_number]
                try:
                    self.results[as_results.results[name_server].entry.as_number][name_server]
                except KeyError:
                    self.results[as_results.results[name_server].entry.as_number][name_server] = ASResolverValueForROVPageScraping.construct_from(as_results.results[name_server])
            except KeyError:
                self.results[as_results.results[name_server].entry.as_number] = dict()
                self.results[as_results.results[name_server].entry.as_number][name_server] = ASResolverValueForROVPageScraping.construct_from(as_results.results[name_server])

