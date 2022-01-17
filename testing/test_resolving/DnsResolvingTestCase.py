import copy
import unittest
from pathlib import Path
import selenium
from entities.resolvers.DnsResolver import DnsResolver
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.scrapers.TLDPageScraper import TLDPageScraper
from entities.error_log.ErrorLogger import ErrorLogger
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError


# DOMAIN NAME LIST EXAMPLES
# ['accounts.google.com', 'login.microsoftonline.com', 'www.facebook.com', 'auth.digidentity.eu', 'clave-dninbrt.seg-social.gob.es', 'pasarela.clave.gob.es', 'unipd.it', 'dei.unipd.it', 'units.it']
# ['accounts.google.com', 'login.microsoftonline.com', 'www.facebook.com', 'auth.digidentity.eu', 'clave-dninbrt.seg-social.gob.es', 'pasarela.clave.gob.es']
# ['unipd.it', 'dei.unipd.it', 'www.units.it', 'units.it', 'dia.units.it']
# ['google.it']
# ['ocsp.digicert.com']
# ['modor.verisign.net']
class DnsResolvingTestCase(unittest.TestCase):
    """
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
    tld_scraper = None
    consider_tld = None
    PRD = None
    domain_names = None
    dns_resolver = None

    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == 'LavoroTesi':
                return current
            else:
                current = current.parent

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_names = ['accounts.google.com', 'login.microsoftonline.com', 'www.facebook.com', 'auth.digidentity.eu', 'clave-dninbrt.seg-social.gob.es', 'pasarela.clave.gob.es', 'unipd.it', 'dei.unipd.it', 'units.it']
        cls.cache_filename = 'cache_from_dns_test'
        cls.error_logs_filename = 'error_logs_from_test'
        cls.consider_tld = True
        # ELABORATION
        cls.PRD = DnsResolvingTestCase.get_project_root_folder()
        if not cls.consider_tld:
            try:
                headless_browser = FirefoxHeadlessWebDriver(cls.PRD)
            except (FileWithExtensionNotFoundError, selenium.common.exceptions.WebDriverException) as e:
                print(f"!!! {str(e)} !!!")
                return
            cls.tld_scraper = TLDPageScraper(headless_browser)
            try:
                tlds = cls.tld_scraper.scrape_tld()
            except (
            selenium.common.exceptions.WebDriverException, selenium.common.exceptions.NoSuchElementException) as e:
                print(f"!!! {str(e)} !!!")
                return
            cls.dns_resolver = DnsResolver(tlds)
            headless_browser.close()
        else:
            cls.dns_resolver = DnsResolver(None)
        cls.dns_resolver.cache.clear()
        print("START DNS DEPENDENCIES RESOLVER")
        cls.dns_results = cls.dns_resolver.resolve_multiple_domains_dependencies(cls.domain_names, reset_cache_per_elaboration=True, consider_tld=cls.consider_tld)
        print("END DNS DEPENDENCIES RESOLVER")
        print("START CACHE DNS DEPENDENCIES RESOLVER")
        cls.dns_cache_results = cls.dns_resolver.resolve_multiple_domains_dependencies(cls.domain_names, reset_cache_per_elaboration=False, consider_tld=cls.consider_tld)
        print("END CACHE DNS DEPENDENCIES RESOLVER")

    def test_1_results_equality_from_cache(self):
        print(f"\n------- [1] START EQUALITY FROM CACHE TEST -------")
        self.assertEqual(self.dns_results.zone_dependencies_per_domain_name.keys(), self.dns_cache_results.zone_dependencies_per_domain_name.keys())
        are_count_keys_same = (len(self.dns_results.zone_dependencies_per_domain_name.keys()) == len(self.dns_cache_results.zone_dependencies_per_domain_name.keys()))
        are_count_values_same = (len(self.dns_results.zone_dependencies_per_domain_name.values()) == len(self.dns_cache_results.zone_dependencies_per_domain_name.values()))
        if are_count_keys_same and not are_count_values_same:
            for domain_name in self.dns_results.zone_dependencies_per_domain_name.keys():
                set_new = set(self.dns_results.zone_dependencies_per_domain_name[domain_name])
                set_old = set(self.dns_cache_results.zone_dependencies_per_domain_name[domain_name])
                set_minor = None
                set_major = None
                are_same = False
                if len(set_new) > len(set_old):
                    set_minor = copy.deepcopy(set_old)
                    set_major = copy.deepcopy(set_new)
                elif len(set_new) == len(set_old):
                    are_same = True
                else:
                    set_minor = copy.deepcopy(set_new)
                    set_major = copy.deepcopy(set_old)
                if not are_same:
                    for elem in set_minor:
                        set_major.remove(elem)
                    for i, elem in enumerate(set_major):
                        print(f"extra[{i + 1}/{len(set_major)}] = {elem}")
                self.assertSetEqual(set_new, set_old)
        elif are_count_keys_same and are_count_values_same:
            print(f"No differences to print.")
        else:
            print(f"Dictionaries keys size are different, cannot print...")
        self.assertSetEqual(set(self.dns_results.zone_dependencies_per_domain_name), set(self.dns_cache_results.zone_dependencies_per_domain_name))
        print(f"------- [1] END EQUALITY FROM CACHE TEST -------")

    def test_2_are_there_duplicates_in_results(self):
        print(f"\n------- [2] START DUPLICATES IN RESULTS TEST -------")
        duplicates = list()
        for i, rr in enumerate(self.dns_results.zone_dependencies_per_domain_name):
            for j, comp in enumerate(self.dns_cache_results.zone_dependencies_per_domain_name):
                if i != j and rr == comp:
                    duplicates.append(rr)
        if len(duplicates) != 0:
            print(f"\n\nPrinting results duplicates (will be doubled):")
            for i, elem in enumerate(duplicates):
                print(f"duplicates[{i+1}] = {str(elem)}")
        print(f"number of duplicates = {len(duplicates)}")
        self.assertEqual(0, len(duplicates))
        print(f"------- [2] END DUPLICATES IN RESULTS TEST -------")

    def test_3_are_there_duplicates_in_cache(self):
        print(f"\n------- [3] START DUPLICATES IN CACHE RESULTS TEST -------")
        duplicates = list()
        for i, rr in enumerate(self.dns_resolver.cache.cache):
            for j, comp in enumerate(self.dns_resolver.cache.cache):
                if i != j and rr == comp:
                    duplicates.append(rr)
        if len(duplicates) != 0:
            print(f"\n\nPrinting cache duplicates (will be doubled):")
            for i, elem in enumerate(duplicates):
                print(f"duplicates[{i+1}] = {str(elem)}")
        print(f"number of duplicates = {len(duplicates)}")
        self.assertEqual(0, len(duplicates))
        print(f"------- [3] END DUPLICATES IN CACHE RESULTS TEST -------")

    def test_4_zone_zone_dependencies_integrity(self):
        print(f"\n------- [4] START CHECK BETWEEN ZONE RESULTS TEST -------")
        print(f"zone dependencies dict keys size = {len(self.dns_results.zone_name_dependencies_per_zone.keys())}")
        print(f"zone dependencies from cache dict keys size = {len(self.dns_results.zone_name_dependencies_per_zone.keys())}")
        are_keys_same = (len(self.dns_results.zone_name_dependencies_per_zone.keys()) == len(self.dns_cache_results.zone_name_dependencies_per_zone.keys()))
        if are_keys_same:
            for i, zone_name in enumerate(self.dns_results.zone_name_dependencies_per_zone.keys()):
                print(f"[{i + 1}/{len(self.dns_results.zone_name_dependencies_per_zone.keys())}] = {zone_name}\t", end='')
                print(f"len(results) = {len(self.dns_results.zone_name_dependencies_per_zone[zone_name])}\t", end='')
                print(f"len(cache_results) = {len(self.dns_cache_results.zone_name_dependencies_per_zone[zone_name])}\t", end='')
                print(f"same? {(len(self.dns_results.zone_name_dependencies_per_zone[zone_name]) == len(self.dns_cache_results.zone_name_dependencies_per_zone[zone_name]))}")
                set_new = set(self.dns_results.zone_name_dependencies_per_zone[zone_name])
                set_old = set(self.dns_cache_results.zone_name_dependencies_per_zone[zone_name])
                set_minor = None
                set_major = None
                are_same = False
                is_cache_one_bigger = None
                if len(set_new) > len(set_old):
                    set_minor = copy.deepcopy(set_old)
                    set_major = copy.deepcopy(set_new)
                    is_cache_one_bigger = False
                elif len(set_new) == len(set_old):
                    are_same = True
                else:
                    set_minor = copy.deepcopy(set_new)
                    set_major = copy.deepcopy(set_old)
                    is_cache_one_bigger = True
                if not are_same:
                    if is_cache_one_bigger:
                        print(f"The cache one has more values:")
                    else:
                        print(f"The normal one has more values:")
                    for elem in set_minor:
                        set_major.remove(elem)
                    for i, elem in enumerate(set_major):
                        print(f"extra[{i+1}/{len(set_major)}] = {elem}")
                self.assertSetEqual(set_new, set_old)
        else:
            print(f"Dictionaries keys size are different...")
            set_key_new = set(self.dns_results.zone_name_dependencies_per_zone.keys())
            set_key_old = set(self.dns_cache_results.zone_name_dependencies_per_zone.keys())
            result = set_key_new.difference(set_key_old)
            if len(result) != 0:
                print(f"Elements that the normal dictionary keys has more than the cache one:")
                for i, elem in enumerate(result):
                    print(f"[{i+1}] = {elem}")
            else:
                result = set_key_old.difference(set_key_new)
                print(f"Elements that the cache dictionary keys has more than the normal one:")
                for i, elem in enumerate(result):
                    print(f"[{i+1}] = {elem}")
        self.assertEqual(self.dns_results.zone_name_dependencies_per_zone.keys(), self.dns_cache_results.zone_name_dependencies_per_zone.keys())
        print(f"------- [4] END CHECK BETWEEN ZONE RESULTS TEST -------")

    # FIXME: bug
    def test_5_nameservers_zone_dependencies_integrity(self):
        print(f"\n------- [5] START CHECK BETWEEN NAMESERVER RESULTS TEST -------")
        print(f"nameservers dict keys size = {len(self.dns_results.zone_name_dependencies_per_name_server.keys())}")
        print(f"nameservers from cache dict keys size = {len(self.dns_results.zone_name_dependencies_per_name_server.keys())}")
        are_keys_same = (len(self.dns_results.zone_name_dependencies_per_name_server.keys()) == len(self.dns_cache_results.zone_name_dependencies_per_name_server.keys()))
        if are_keys_same:
            for i, nameserver in enumerate(self.dns_results.zone_name_dependencies_per_name_server.keys()):
                print(f"[{i + 1}/{len(self.dns_results.zone_name_dependencies_per_name_server.keys())}] = {nameserver}\t", end='')
                print(f"len(results) = {len(self.dns_results.zone_name_dependencies_per_name_server[nameserver])}\t", end='')
                print(f"len(cache_results) = {len(self.dns_cache_results.zone_name_dependencies_per_name_server[nameserver])}\t", end='')
                print(f"same? {(len(self.dns_results.zone_name_dependencies_per_name_server[nameserver]) == len(self.dns_cache_results.zone_name_dependencies_per_name_server[nameserver]))}")
                set_new = set(self.dns_results.zone_name_dependencies_per_name_server[nameserver])
                set_old = set(self.dns_cache_results.zone_name_dependencies_per_name_server[nameserver])
                set_minor = None
                set_major = None
                are_same = False
                is_cache_one_bigger = None
                if len(set_new) > len(set_old):
                    set_minor = copy.deepcopy(set_old)
                    set_major = copy.deepcopy(set_new)
                    is_cache_one_bigger = False
                elif len(set_new) == len(set_old):
                    are_same = True
                else:
                    set_minor = copy.deepcopy(set_new)
                    set_major = copy.deepcopy(set_old)
                    is_cache_one_bigger = True
                if not are_same:
                    if is_cache_one_bigger:
                        print(f"The cache one has more values:")
                    else:
                        print(f"The normal one has more values:")
                    for elem in set_minor:
                        set_major.remove(elem)
                    for i, elem in enumerate(set_major):
                        print(f"extra[{i+1}/{len(set_major)}] = {elem}")
                self.assertSetEqual(set_new, set_old)
        else:
            print(f"Dictionaries keys size are different...")
            set_key_new = set(self.dns_results.zone_name_dependencies_per_name_server.keys())
            set_key_old = set(self.dns_cache_results.zone_name_dependencies_per_name_server.keys())
            result = set_key_new.difference(set_key_old)
            if len(result) != 0:
                print(f"Elements that the normal dictionary keys has more than the cache one:")
                for i, elem in enumerate(result):
                    print(f"[{i+1}] = {elem}")
            else:
                result = set_key_old.difference(set_key_new)
                print(f"Elements that the cache dictionary keys has more than the normal one:")
                for i, elem in enumerate(result):
                    print(f"[{i+1}] = {elem}")
        self.assertEqual(self.dns_results.zone_name_dependencies_per_name_server.keys(), self.dns_cache_results.zone_name_dependencies_per_name_server.keys())
        print(f"------- [5] END CHECK BETWEEN NAMESERVER RESULTS TEST -------")

    def test_6_presence_of_every_nameserver(self):
        print(f"\n------- [6] START PRESENCE OF NAMESERVERS TEST -------")
        zone_list_nameservers = set()
        for zone_list in self.dns_results.zone_dependencies_per_domain_name.values():
            for zone in zone_list:
                zone_nameservers_set = set(zone.nameservers)
                zone_list_nameservers = zone_list_nameservers.union(zone_nameservers_set)
        nameserver_presence = dict()
        for i, nameserver in enumerate(self.dns_results.zone_name_dependencies_per_name_server.keys()):
            if nameserver in zone_list_nameservers:
                nameserver_presence[nameserver] = True
            else:
                nameserver_presence[nameserver] = False
            print(f"nameserver[{i + 1}/{len(self.dns_results.zone_name_dependencies_per_name_server.keys())}]: {nameserver} is present? {nameserver_presence[nameserver]}")
        for nameserver in nameserver_presence.keys():
            self.assertTrue(nameserver_presence[nameserver])
        print(f"------- [6] END PRESENCE OF NAMESERVERS TEST -------")

    def test_7_presence_of_every_zone(self):
        print(f"\n------- [7] START PRESENCE OF ZONES TEST -------")
        zones_names_set = set()
        for zone_list in self.dns_results.zone_dependencies_per_domain_name.values():
            zone_names_set = set(map(lambda z: z.name, zone_list))
            zones_names_set = zones_names_set.union(zone_names_set)
        zone_presence = dict()
        for i, zone_name in enumerate(self.dns_results.zone_name_dependencies_per_zone.keys()):
            if zone_name in zones_names_set:
                zone_presence[zone_name] = True
            else:
                zone_presence[zone_name] = False
            print(f"nameserver[{i + 1}/{len(self.dns_results.zone_name_dependencies_per_zone.keys())}]: {zone_name} is present? {zone_presence[zone_name]}")
        for nameserver in zone_presence.keys():
            self.assertTrue(zone_presence[nameserver])
        print(f"------- [7] END PRESENCE OF ZONES TEST -------")

    def test_8_presence_of_every_addresses(self):
        print(f"\n------- [8] START PRESENCE OF ADDRESSES TEST -------")
        zone_set = set()
        for zone_list in self.dns_results.zone_dependencies_per_domain_name.values():
            for zone in zone_list:
                zone_set.add(zone)
        for zone in zone_set:
            count_nameservers = 0
            count_rr_addresses = 0
            for nameserver in zone.nameservers:
                count_nameservers = count_nameservers + 1
            for rr in zone.addresses:
                count_rr_addresses = count_rr_addresses + 1
            self.assertEqual(count_nameservers, count_rr_addresses)

        zone_set = set()
        for zone_list in self.dns_cache_results.zone_dependencies_per_domain_name.values():
            for zone in zone_list:
                zone_set.add(zone)
        for zone in zone_set:
            count_nameservers = 0
            count_rr_addresses = 0
            for nameserver in zone.nameservers:
                count_nameservers = count_nameservers + 1
            for rr in zone.addresses:
                count_rr_addresses = count_rr_addresses + 1
            self.assertEqual(count_nameservers, count_rr_addresses)
        print(f"------- [8] END PRESENCE OF ADDRESSES TEST -------")

    def test_9_export_results(self):
        self.dns_resolver.cache.write_to_csv_in_output_folder(filename=self.cache_filename, project_root_directory=self.PRD)
        print(f"\n**** cache written in 'output' folder: file is named 'cache_from_dns_test.csv'")
        logger = ErrorLogger()
        for log in self.dns_results.error_logs:
            logger.add_entry(log)
        logger.write_to_csv_in_output_folder(filename=self.error_logs_filename, project_root_directory=self.PRD)
        print(f"\n**** error_logs written in 'output' folder: file is named 'error_logs_from_test.csv'\n")


if __name__ == '__main__':
    unittest.main()
