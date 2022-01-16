import ipaddress
import unittest
from pathlib import Path
import selenium
from peewee import DoesNotExist
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.resolvers.DnsResolver import DnsResolver
from entities.resolvers.IpAsDatabase import IpAsDatabase
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from entities.resolvers.results.AutonomousSystemResolutionResults import AutonomousSystemResolutionResults
from entities.resolvers.results.MultipleDnsZoneDependenciesResult import MultipleDnsZoneDependenciesResult
from entities.scrapers.ROVPageScraper import ROVPageScraper
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError
from persistence import helper_application_results, helper_ip_address, helper_name_server, helper_ip_network, \
    helper_autonomous_system, helper_rov, helper_prefixes_table


class IpAsAndROVIntegrityTestCase(unittest.TestCase):
    """
    Test class
    """
    final_results = None
    persist_errors = None
    dns_results = None
    domain_name_list = None
    headless_browser = None

    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == 'LavoroTesi':
                return current
            else:
                current = current.parent

    @staticmethod
    def do_ip_as_database_resolving(ip_as_resolver: IpAsDatabase, dns_results: MultipleDnsZoneDependenciesResult) -> AutonomousSystemResolutionResults:
        print("\n\nSTART IP-AS RESOLVER")
        results = AutonomousSystemResolutionResults()
        zone_obj_dict = dict()
        for domain_name in dns_results.zone_dependencies_per_domain_name.keys():
            for zone in dns_results.zone_dependencies_per_domain_name[domain_name]:
                try:
                    zone_obj_dict[zone.name]
                except KeyError:
                    zone_obj_dict[zone.name] = zone
        for index_domain, domain in enumerate(dns_results.zone_dependencies_per_domain_name.keys()):
            print(f"Handling domain[{index_domain}] '{domain}'")
            for index_zone, zone in enumerate(dns_results.zone_dependencies_per_domain_name[domain]):
                print(f"--> Handling zone[{index_zone}] '{zone.name}'")
                for i, nameserver in enumerate(zone.nameservers):
                    results.add_name_server(nameserver)
                    try:
                        # TODO: gestire più indirizzi per nameserver
                        try:
                            rr = zone.resolve_nameserver(nameserver)
                        except NoAvailablePathError:
                            results.set_name_server_to_none(nameserver)
                            continue
                        ip = ipaddress.IPv4Address(rr.get_first_value())  # no exception catch needed
                        results.insert_ip_address(nameserver, ip)
                        entry = ip_as_resolver.resolve_range(ip)
                        results.insert_ip_as_entry(nameserver, entry)
                        try:
                            belonging_network_ip_as_db, networks = entry.get_network_of_ip(ip)
                            print(
                                f"----> for nameserver[{i}] '{nameserver}' ({ip.compressed}) found AS{str(entry.as_number)}: [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. Belonging network: {belonging_network_ip_as_db.compressed}")
                            results.insert_belonging_network(nameserver, belonging_network_ip_as_db)
                        except ValueError as exc:
                            print(
                                f"----> for nameserver[{i}] '{nameserver}' ({ip.compressed}) found AS record: [{entry}]")
                            results.insert_belonging_network(nameserver, None)
                    except AutonomousSystemNotFoundError as exc:
                        print(f"----> for nameserver[{i}] '{nameserver}' ({ip.compressed}) no AS found.")
                        results.insert_ip_as_entry(nameserver, None)
                        results.insert_belonging_network(nameserver, None)
        print("END IP-AS RESOLVER")
        return results

    @staticmethod
    def do_rov_page_scraping(rov_page_scraper: ROVPageScraper, reformat: ASResolverResultForROVPageScraping) -> ASResolverResultForROVPageScraping:
        print("\n\nSTART ROV PAGE SCRAPING")
        for as_number in reformat.results.keys():
            print(f"Loading page for AS{as_number}")
            try:
                rov_page_scraper.load_as_page(as_number)
            except selenium.common.exceptions.WebDriverException as exc:
                print(f"!!! {str(exc)} !!!")
                reformat.results[as_number] = None
                continue
            except (TableNotPresentError, ValueError, TableEmptyError, NotROVStateTypeError) as exc:
                print(f"!!! {str(exc)} !!!")
                reformat.results[as_number] = None
                continue
            for nameserver in reformat.results[as_number].keys():
                ip_string = reformat.results[as_number][nameserver].ip_address
                entry_ip_as_db = reformat.results[as_number][nameserver].entry_as_database
                belonging_network_ip_as_db = reformat.results[as_number][nameserver].belonging_network
                try:
                    row = rov_page_scraper.get_network_if_present(ipaddress.ip_address(ip_string))  # non gestisco ValueError perché non può accadere qua
                    reformat.results[as_number][nameserver].insert_rov_entry(row)
                    print(f"--> for '{nameserver}' ({ip_string}), found row: {str(row)}")
                except (TableNotPresentError, TableEmptyError, NetworkNotFoundError) as exc:
                    print(f"!!! {exc.message} !!!")
                    reformat.results[as_number][nameserver].insert_rov_entry(None)
        print("END ROV PAGE SCRAPING")
        return reformat

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_name_list = ['unipd.it', 'google.it', 'youtube.it']
        cls.persist_errors = True
        # ELABORATION
        PRD = IpAsAndROVIntegrityTestCase.get_project_root_folder()
        dns_resolver = DnsResolver(None)
        cls.dns_results = dns_resolver.resolve_multiple_domains_dependencies(cls.domain_name_list)
        ip_as_resolver = IpAsDatabase(project_root_directory=PRD)
        ip_as_results = IpAsAndROVIntegrityTestCase.do_ip_as_database_resolving(ip_as_resolver, cls.dns_results)
        rov_scraper_pre_results = ASResolverResultForROVPageScraping(ip_as_results)
        cls.headless_browser = FirefoxHeadlessWebDriver(PRD)
        rov_scraper = ROVPageScraper(cls.headless_browser)
        cls.final_results = IpAsAndROVIntegrityTestCase.do_rov_page_scraping(rov_scraper, rov_scraper_pre_results)
        print("\nInsertion into database... ", end="")
        for as_number in cls.final_results.results.keys():
            if cls.final_results.results[as_number] is None:
                print('')
                pass
            for name_server in cls.final_results.results[as_number].keys():
                helper_name_server.insert(name_server)
        helper_application_results.insert_ip_as_and_rov_resolving(cls.final_results, persist_errors=cls.persist_errors)
        print(f"DONE.")

    def test_1_integrity(self):
        print("\n------- [1] START INTEGRITY TEST -------")
        for as_number in self.final_results.results.keys():
            print(f"AS{as_number}:")
            for name_server in self.final_results.results[as_number].keys():
                print(f"--> nameserver: {name_server}")
                res = self.final_results.results[as_number][name_server]
                if res.ip_address is None:
                    ip_address_elaboration = None
                else:
                    ip_address_elaboration = res.ip_address.exploded
                if res.entry_as_database is None:
                    as_elaboration_number = None
                else:
                    as_elaboration_number = res.entry_as_database.as_number
                if res.entry_rov_page is None:
                    rov_elaboration_state = None
                else:
                    rov_elaboration_state = res.entry_rov_page.rov_state.to_string()
                if res.belonging_network is None:
                    ip_network_elaboration = None
                else:
                    ip_network_elaboration = res.belonging_network.compressed
                print(f"----> Results from elaboration:")
                print(f"------> ip: {ip_address_elaboration}")
                print(f"------> entry_ip_as: {as_elaboration_number}")
                print(f"------> entry_rov_page: {rov_elaboration_state}")
                print(f"------> network: {ip_network_elaboration}")
                print(f"----> Results from database:")
                try:
                    temp = helper_ip_address.get_first_of(name_server)
                    ip_address_compressed = temp.exploded_notation
                    print(f"------> ip: {ip_address_compressed}")
                    try:
                        tmp = helper_ip_network.get(ip_address_compressed)
                        ip_network_db = tmp.compressed_notation
                        print(f"------> network: {ip_network_db}")
                        try:
                            as_db = helper_autonomous_system.get_first_of(ip_network_db)
                            as_db_number = as_db.number
                            print(f"------> as: AS{as_db_number}")
                        except DoesNotExist:
                            as_db_number = None
                            print(f"------> as: NOT FOUND")
                        try:
                            rov_db = helper_rov.get_from_network(ip_network_db)
                            rov_db_state = rov_db.state
                            print(f"------> rov: AS{str(rov_db)}")
                        except DoesNotExist:
                            rov_db_state = None
                            print(f"------> rov: NOT FOUND")
                        self.assertEqual(as_elaboration_number, as_db_number)
                        self.assertEqual(rov_elaboration_state, rov_db_state)
                        self.assertEqual(ip_network_elaboration, ip_network_db)
                    except DoesNotExist:
                        ip_network_db = None
                        print(f"------> network: NOT FOUND")
                except DoesNotExist:
                    ip_address_compressed = None
                    print(f"------> ip: NOT FOUND")
                self.assertEqual(ip_address_elaboration, ip_address_compressed)


        print("------- [1] END INTEGRITY TEST -------")

    def test_2_no_more_than_1_association_for_network(self):
        print("\n------- [2] START NO DUPLICATES FOR EACH NETWORK TEST -------")
        ines = helper_ip_network.get_all()
        for ine in ines:
            ases = helper_autonomous_system.get_all_of(ine)
            self.assertLess(len(ases), 2)
            ptas = helper_prefixes_table.get_all_of(ine)
            self.assertLess(len(ptas), 2)
        print(f"Everything went well.")
        print("------- [2] END NO DUPLICATES FOR EACH NETWORK TEST -------")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
