import unittest
from entities.DomainName import DomainName
from entities.resolvers.DnsResolver import DnsResolver
from entities.error_log.ErrorLogger import ErrorLogger
from utils import file_utils


class ZoneDependenciesResolvingCase(unittest.TestCase):
    """
    DEFINITIVE TEST
    This class purpose is to provide some instruments to test the behaviour of the DNS resolver.
    The input to set is a list of domain name (PARAMETER), the name of the cache file to export and the name of the
    error logs file to export.
    The elaboration is divided in 2 parts: the first executes the domain name list parameter clearing cache per domain
    name, the second executes the same domain name list parameter without clearing cache; the idea is to have the same
    results both ways: from cache and from queries.
    In the end these tests are computed:

    1- everything is exported in the output folder of the project root directory (PRD)

    2- the integrity between results from queries and cache is checked: if there's no match, then the elements that
    overflows with respect to the other result will be printed

    3- check to control if there are duplicates in the results from queries

    4- check if cache contains duplicates

    5- check integrity of zone dependencies between zones dictionary from queries and from cache. If there's no match
    in the key set, then the values that overflows with respect to the other result will be printed

    6- check integrity of zone dependencies between nameservers dictionary from queries and from cache. If there's no
    match in the key set, then the values that overflows with respect to the other result will be printed

    """
    consider_tld = None
    PRD = None
    domain_names = None
    dns_resolver = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        domain_name_strings = ['pec.comune.bologna.it.']
        domain_name_strings = ['www.dradis.netflix.com', 'www.us-east-1.internal.dradis.netflix.com.']
        cls.cache_filename = 'cache_from_dns_test'
        cls.error_logs_filename = 'error_logs_from_test'
        cls.consider_tld = False
        cls.perform_zone_dependencies = True
        cls.perform_name_server_dependencies = True
        # ELABORATION
        cls.domain_names = DomainName.from_string_list(domain_name_strings)
        cls.PRD = file_utils.get_project_root_directory()
        cls.dns_resolver = DnsResolver(cls.consider_tld)
        cls.dns_resolver.cache.clear()
        print("START AUTHORITATIVE DNS DEPENDENCIES RESOLVER")
        cls.dns_authoritative_results = cls.dns_resolver.resolve_multiple_domains_dependencies(cls.domain_names, reset_cache_per_elaboration=True)
        print("END AUTHORITATIVE DNS DEPENDENCIES RESOLVER")
        print("\n\n")
        print("START CACHE DNS DEPENDENCIES RESOLVER")
        cls.dns_cache_results = cls.dns_resolver.resolve_multiple_domains_dependencies(cls.domain_names, reset_cache_per_elaboration=False)
        print("END CACHE DNS DEPENDENCIES RESOLVER")

    def test_01_results_equality_from_cache(self):
        print(f"\n------- [1] START EQUALITY FROM CACHE TEST -------")
        print(f"authoritative results: {len(self.dns_authoritative_results.zone_dependencies_per_domain_name.keys())} domain names")
        print(f"cache results: {len(self.dns_cache_results.zone_dependencies_per_domain_name.keys())} domain names")
        self.assertSetEqual(set(self.dns_authoritative_results.zone_dependencies_per_domain_name.keys()), set(self.dns_cache_results.zone_dependencies_per_domain_name.keys()))
        self.assertDictEqual(self.dns_authoritative_results.zone_dependencies_per_domain_name, self.dns_cache_results.zone_dependencies_per_domain_name)
        print(f"------- [1] END EQUALITY FROM CACHE TEST -------")

    def test_02_zone_zone_dependencies_integrity(self):
        print(f"\n------- [2] START CHECK BETWEEN ZONE RESULTS TEST -------")
        print(f"authoritative results: {len(self.dns_authoritative_results.zone_dependencies_per_zone.keys())} zones")
        print(f"cache results: {len(self.dns_cache_results.zone_dependencies_per_zone.keys())} zones")
        self.assertSetEqual(set(self.dns_authoritative_results.zone_dependencies_per_zone.keys()), set(self.dns_cache_results.zone_dependencies_per_zone.keys()))
        self.assertDictEqual(self.dns_authoritative_results.zone_dependencies_per_zone, self.dns_cache_results.zone_dependencies_per_zone)
        print(f"------- [2] END CHECK BETWEEN ZONE RESULTS TEST -------")

    def test_03_nameservers_zone_dependencies_integrity(self):
        print(f"\n------- [3] START CHECK BETWEEN NAMESERVER RESULTS TEST -------")
        print(f"authoritative results: {len(self.dns_authoritative_results.zone_dependencies_per_name_server.keys())} nameservers")
        print(f"cache results: {len(self.dns_cache_results.zone_dependencies_per_name_server.keys())} nameservers")
        set_auth = set(self.dns_authoritative_results.zone_dependencies_per_name_server.keys())
        set_cache = set(self.dns_cache_results.zone_dependencies_per_name_server.keys())
        for elem in set_cache:
            if elem not in set_auth:
                print(f"IT'S = {elem}")
        self.assertSetEqual(set(self.dns_authoritative_results.zone_dependencies_per_name_server.keys()), set(self.dns_cache_results.zone_dependencies_per_name_server.keys()))
        self.assertDictEqual(self.dns_authoritative_results.zone_dependencies_per_name_server, self.dns_authoritative_results.zone_dependencies_per_name_server)
        print(f"------- [3] END CHECK BETWEEN NAMESERVER RESULTS TEST -------")

    def test_04_zone_dependencies_integrity_of_each_zone(self):
        if not self.perform_zone_dependencies:
            self.skipTest('')
        print(f"\n------- [4] START ZONE DEPENDENCIES OF ZONES INTEGRITY TEST -------")
        all_zones = set()
        for domain_name in self.dns_authoritative_results.zone_dependencies_per_domain_name.keys():
            all_zones = all_zones.union(self.dns_authoritative_results.zone_dependencies_per_domain_name[domain_name])
        for domain_name in self.dns_cache_results.zone_dependencies_per_domain_name.keys():
            all_zones = all_zones.union(self.dns_cache_results.zone_dependencies_per_domain_name[domain_name])
        print(f"Total number of zones: {len(all_zones)}\n")
        for i, zone in enumerate(all_zones):
            print(f"Resolving dependencies of zone[{i+1}/{len(all_zones)}]: {zone.name}")
            current_result = self.dns_resolver.resolve_domain_dependencies(zone.name)
            current_result.zone_dependencies.remove(zone)
            self.assertSetEqual(current_result.zone_dependencies, self.dns_authoritative_results.zone_dependencies_per_zone[zone])
        print(f"------- [4] END ZONE DEPENDENCIES OF ZONES INTEGRITY TEST -------")

    def test_05_zone_dependencies_integrity_of_each_name_server(self):
        if not self.perform_name_server_dependencies:
            self.skipTest('')
        print(f"\n------- [5] START ZONE DEPENDENCIES OF NAMESERVERS INTEGRITY TEST -------")
        all_name_servers = set()
        for name_server in self.dns_authoritative_results.zone_dependencies_per_name_server.keys():
            all_name_servers.add(name_server)
        for name_server in self.dns_cache_results.zone_dependencies_per_name_server.keys():
            all_name_servers.add(name_server)
        print(f"total number of nameservers: {len(all_name_servers)}")
        for i, name_server in enumerate(all_name_servers):
            print(f"Resolving dependencies of nameserver[{i + 1}/{len(all_name_servers)}]: {name_server}")
            current_result = self.dns_resolver.resolve_domain_dependencies(name_server)
            self.assertSetEqual(current_result.zone_dependencies, self.dns_authoritative_results.zone_dependencies_per_name_server[name_server])
        print(f"------- [5] END ZONE DEPENDENCIES OF NAMESERVERS INTEGRITY TEST -------")

    def test_06_export_results(self):
        self.dns_resolver.cache.write_to_csv_in_output_folder(filename=self.cache_filename, project_root_directory=self.PRD)
        print(f"\n**** cache written in 'output' folder: file is named '{self.cache_filename}'")
        logger = ErrorLogger()
        for log in self.dns_authoritative_results.error_logs:
            logger.add_entry(log)
        logger.write_to_csv_in_output_folder(filename=self.error_logs_filename, project_root_directory=self.PRD)
        print(f"\n**** error_logs written in 'output' folder: file is named '{self.error_logs_filename}'")


if __name__ == '__main__':
    unittest.main()
