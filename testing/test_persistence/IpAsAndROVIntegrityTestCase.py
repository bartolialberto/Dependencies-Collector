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
from exceptions.EmptyResultError import EmptyResultError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NoAliasFoundError import NoAliasFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError
from persistence import helper_application_results, helper_ip_address, helper_name_server, helper_ip_network, \
    helper_autonomous_system, helper_rov, helper_prefixes_table, helper_ip_range_tsv, helper_ip_range_rov, helper_alias


class IpAsAndROVIntegrityTestCase(unittest.TestCase):
    """
    Test class that takes a list of domain names in input and executes: DNS resolving, IP-AS resolving and in the end
    ROVPage scraping. Then tests are done to check data integrity of ROVPage scraping (which are linked to the IP-AS
    resolution obviously).

    """
    final_results = None
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
        for index_domain, domain in enumerate(dns_results.zone_dependencies_per_domain_name.keys()):
            print(f"Handling domain[{index_domain}] '{domain}'")
            for index_zone, zone in enumerate(dns_results.zone_dependencies_per_domain_name[domain]):
                print(f"--> Handling zone[{index_zone}] '{zone.name}'")
                for i, nameserver in enumerate(zone.nameservers):
                    try:
                        rr_a = zone.resolve_name_server_access_path(nameserver)
                    except NoAvailablePathError:
                        print(f"!!! NO RESOLVED IP ADDRESS FROM name server: {nameserver} !!!")
                        continue
                    for ip_string in rr_a.values:
                        results.add_ip_address(ip_string)
                        results.insert_name_server(ip_string, nameserver)
                        ip = ipaddress.IPv4Address(ip_string)        # no exception catch needed
                        try:
                            entry = ip_as_resolver.resolve_range(ip)
                        except (AutonomousSystemNotFoundError, ValueError) as e:
                            results.insert_ip_as_entry(ip, None)
                            results.insert_ip_range_tsv(ip, None)
                            print(f"!!! {str(e)} !!!")
                            continue
                        results.insert_ip_as_entry(ip_string, entry)
                        try:
                            belonging_network_ip_as_db, networks = entry.get_network_of_ip(ip)
                            print(f"----> for {ip.compressed} ({nameserver}) found AS{str(entry.as_number)}: [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. Belonging network: {belonging_network_ip_as_db.compressed}")
                            results.insert_ip_range_tsv(ip_string, belonging_network_ip_as_db)
                        except ValueError as exc:
                            print(f"----> for {ip.compressed} ({nameserver}) found AS record: [{str(entry)}]")
                            results.insert_ip_range_tsv(ip_string, None)
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
            for ip_address in reformat.results[as_number].keys():
                name_server = reformat.results[as_number][ip_address].server
                entry_ip_as_db = reformat.results[as_number][ip_address].entry_as_database
                belonging_network_ip_as_db = reformat.results[as_number][ip_address].ip_range_tsv
                try:
                    row = rov_page_scraper.get_network_if_present(ipaddress.ip_address(ip_address))  # non gestisco ValueError perché non può accadere qua
                    reformat.results[as_number][ip_address].insert_rov_entry(row)
                    print(f"--> for {ip_address} ({name_server}) found row: {str(row)}")
                except (TableNotPresentError, TableEmptyError, NetworkNotFoundError) as exc:
                    print(f"!!! {exc.message} !!!")
                    reformat.results[as_number][ip_address].insert_rov_entry(None)
        print("END ROV PAGE SCRAPING")
        return reformat

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_name_list = ['unipd.it', 'google.it', 'youtube.it']
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
        helper_application_results.insert_dns_result(cls.dns_results)
        helper_application_results.insert_ip_as_and_rov_resolving(cls.final_results)
        print(f"DONE.")

    def test_1_integrity(self):
        print("\n------- [1] START INTEGRITY TEST -------")
        for as_number in self.final_results.results.keys():
            print(f"AS{as_number}:")
            if self.final_results.results[as_number] is None:
                print('')
                continue
            for ip_address in self.final_results.results[as_number].keys():
                print(f"--> IP address: {ip_address}")
                res = self.final_results.results[as_number][ip_address]
                if res.server is None:
                    name_server_elaboration = None
                else:
                    name_server_elaboration = res.server
                if res.entry_rov_page is None:
                    rov_elaboration_state = None
                else:
                    rov_elaboration_state = res.entry_rov_page.rov_state.to_string()
                if res.entry_rov_page is None:
                    ip_range_rov_elaboration = None
                else:
                    ip_range_rov_elaboration = res.entry_rov_page.prefix.compressed
                if res.ip_range_tsv is None:
                    ip_range_tsv_elaboration = None
                else:
                    ip_range_tsv_elaboration = res.ip_range_tsv.compressed
                print(f"----> Results from elaboration:")
                print(f"------> name_server: {name_server_elaboration}")
                print(f"------> ip_range_tsv: {ip_range_tsv_elaboration}")
                print(f"------> ip_range_rov: {ip_range_rov_elaboration}")
                print(f"------> entry_rov_page_state: {rov_elaboration_state}")
                # we can't get the name server from the IP address, because there is the case in which name server is an
                # alias of the domain name that resolved such IP address
                try:
                    nses = helper_name_server.get_all_from_ip_address(ip_address)
                    if len(nses) > 1:
                        self.fail(f"ERROR: address: {ip_address} has more than 1 name server associated")
                    nse = nses[0]
                    domain_name_that_resolves_in_address = nse.name
                    try:
                        name_servers_db = helper_alias.get_all_aliases_from_name(domain_name_that_resolves_in_address)
                    except (NoAliasFoundError, DoesNotExist):
                        name_servers_db = set()
                        name_servers_db.add(domain_name_that_resolves_in_address)
                except (DoesNotExist, EmptyResultError):
                    domain_name_that_resolves_in_address = None
                    name_servers_db = set()
                try:
                    irtes = helper_ip_range_tsv.get_all_from(ip_address)
                    if len(irtes) > 1:
                        self.fail(f"ERROR: address: {ip_address} has more than 1 ip range tsv associated")
                    irte = irtes[0]
                    ip_range_tsv_db = irte.compressed_notation
                except (DoesNotExist, EmptyResultError):
                    ip_range_tsv_db = None
                try:
                    irres = helper_ip_range_rov.get_all_from(ip_address)
                    if len(irres) > 1:
                        self.fail(f"ERROR: address: {ip_address} has more than 1 ip range rov associated")
                    irre = irres[0]
                    ip_range_rov_db = irre.compressed_notation
                except (DoesNotExist, EmptyResultError):
                    ip_range_rov_db = None
                try:
                    res = helper_rov.get_all_from(ip_address, with_ip_range_rov_string=False)
                    if len(res) > 1:
                        self.fail(f"ERROR: address: {ip_address} has more than 1 ip range rov associated")
                    re = res[0]
                    rov_state_db = re.state
                except (DoesNotExist, EmptyResultError):
                    rov_state_db = None
                print(f"----> Results from database:")
                print(f"------> possible name_servers: {str(name_servers_db)}")
                print(f"------> ip_range_tsv: {ip_range_tsv_db}")
                print(f"------> ip_range_rov: {ip_range_rov_db}")
                print(f"------> entry_rov_page_state: {rov_state_db}")
                self.assertIn(name_server_elaboration, name_servers_db)     # TODO: fare un metodo che risale i backward aliases
                self.assertEqual(ip_range_tsv_elaboration, ip_range_tsv_db)
                self.assertEqual(ip_range_rov_elaboration, ip_range_rov_db)
                self.assertEqual(rov_elaboration_state, rov_state_db)
        print("------- [1] END INTEGRITY TEST -------")

    def test_2_no_more_than_one_association_for_network(self):
        print("\n------- [2] START NO DUPLICATES FOR EACH NETWORK TEST -------")
        ines = helper_ip_network.get_all()
        pass
        print(f"Everything went well.")
        print("------- [2] END NO DUPLICATES FOR EACH NETWORK TEST -------")


    def test_3_no_more_than_one_domain_name_for_ip_address(self):
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
