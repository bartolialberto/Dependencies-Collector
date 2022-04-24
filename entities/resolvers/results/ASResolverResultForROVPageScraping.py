from entities.resolvers.results.ASResolverValueForROVPageScraping import ASResolverValueForROVPageScraping
from entities.resolvers.results.AutonomousSystemResolutionResults import AutonomousSystemResolutionResults


class ASResolverResultForROVPageScraping:
    """
    This class represents a reformatted AutonomousSystemResolutionResults object. This reformat consists 3 different
    dictionaries:

    1- results: this dictionary consists in reverting the dictionary of results that are resolved completely (it means
    that from the IP address we got the server, the entry from the IP-AS database and the IP range tsv even
    if it is not found [None value]) belonging to the AutonomousSystemResolutionResults object in a manner that uses the
    autonomous system's number as keys, then the associated value to such key is another dictionary that uses IP
    addresses as keys; the latter dictionary then associate such keys to a collection of infos, that are all 'contained'
    in a ASResolverValueForROVPageScraping object.

    2- no_as_results: this dictionary is used to save the IP addresses that didn't resolved in the IP-AS database. It
    uses IP address as key and for value the server name.

    2- unresolved_servers: this set is used to save the servers that didn't resolved even in a IP address.

    ...

    Attributes
    ----------
    results : Dict[str, ASResolverValueForROVPageScraping]
        The reformatted dictionary containing the completely resolved results.
    no_as_results : Dict[str, str]
        The reformatted dictionary containing the results that didn't have a resolution from the IP-AS database.
    unresolved_servers : Set[str]
        The reformatted dictionary.
    """
    def __init__(self, as_results: AutonomousSystemResolutionResults):
        """
        Initialize the object reformatting a AutonomousSystemResolutionResults object.

        :param as_results: An AutonomousSystemResolutionResults object.
        :type as_results: AutonomousSystemResolutionResults
        """
        self.results = dict()
        self.no_as_results = dict()
        self.unresolved_servers = set()

        for ip_address in as_results.complete_results.keys():
            server = as_results.complete_results[ip_address][0]
            entry_ip_as_database = as_results.complete_results[ip_address][1]
            ip_range_tsv = as_results.complete_results[ip_address][2]
            try:
                self.results[entry_ip_as_database.as_number]
                try:
                    self.results[entry_ip_as_database.as_number][ip_address]
                except KeyError:
                    self.results[entry_ip_as_database.as_number][ip_address] = ASResolverValueForROVPageScraping(server, entry_ip_as_database, ip_range_tsv)
            except KeyError:
                self.results[entry_ip_as_database.as_number] = dict()
                self.results[entry_ip_as_database.as_number][ip_address] = ASResolverValueForROVPageScraping(server, entry_ip_as_database, ip_range_tsv)

        for ip_address in as_results.no_ip_range_tsv_results.keys():
            server = as_results.no_ip_range_tsv_results[ip_address][0]
            entry_ip_as_database = as_results.no_ip_range_tsv_results[ip_address][1]
            try:
                self.results[entry_ip_as_database.as_number]
                try:
                    self.results[entry_ip_as_database.as_number][ip_address]
                except KeyError:
                    self.results[entry_ip_as_database.as_number][ip_address] = ASResolverValueForROVPageScraping(server, entry_ip_as_database, None)
            except KeyError:
                self.results[entry_ip_as_database.as_number] = dict()
                self.results[entry_ip_as_database.as_number][ip_address] = ASResolverValueForROVPageScraping(server, entry_ip_as_database, None)

        # get IP from name server of a zone but can't resolve that in the .tsv database
        self.no_as_results = as_results.no_as_results

        # get name server from a zone but can't resolve the IP address
        self.unresolved_servers = as_results.unresolved_servers
