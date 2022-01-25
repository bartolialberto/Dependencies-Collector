import ipaddress
import unittest
from pathlib import Path
import selenium
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.resolvers.DnsResolver import DnsResolver
from entities.resolvers.IpAsDatabase import IpAsDatabase
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from entities.resolvers.results.AutonomousSystemResolutionResults import AutonomousSystemResolutionResults
from entities.scrapers.ROVPageScraper import ROVPageScraper
from exceptions import TableEmptyError
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableNotPresentError import TableNotPresentError


class ROVScrapingResolvingTestCase(unittest.TestCase):
    headless_browser = None
    domain_names = None

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
        cls.domain_names = ['google.it']
        # ELABORATION
        PRD = ROVScrapingResolvingTestCase.get_project_root_folder()
        dns_resolver = DnsResolver(None)
        dns_results = dns_resolver.resolve_multiple_domains_dependencies(cls.domain_names)
        ip_as_resolver = IpAsDatabase(PRD)
        ip_as_results = AutonomousSystemResolutionResults()
        for index_domain, domain in enumerate(dns_results.zone_dependencies_per_domain_name.keys()):
            print(f"Handling domain[{index_domain}] '{domain}'")
            for index_zone, zone in enumerate(dns_results.zone_dependencies_per_domain_name[domain]):
                print(f"--> Handling zone[{index_zone}] '{zone.name}'")
                for i, nameserver in enumerate(zone.nameservers):
                    ip_as_results.add_name_server(nameserver)
                    try:
                        # TODO: gestire più indirizzi per nameserver
                        try:
                            rr = zone.resolve_name_server_access_path(nameserver)
                        except NoAvailablePathError:
                            ip_as_results.set_name_server_to_none(nameserver)
                            continue
                        ip = ipaddress.IPv4Address(rr.get_first_value())  # no exception catch needed
                        ip_as_results.insert_ip_address(nameserver, ip)
                        entry = ip_as_resolver.resolve_range(ip)
                        ip_as_results.insert_ip_as_entry(nameserver, entry)
                        try:
                            belonging_network_ip_as_db, networks = entry.get_network_of_ip(ip)
                            print(
                                f"----> for nameserver[{i}] '{nameserver}' ({ip.compressed}) found AS{str(entry.as_number)}: [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. Belonging network: {belonging_network_ip_as_db.compressed}")
                            ip_as_results.insert_ip_range_tsv(nameserver, belonging_network_ip_as_db)
                        except ValueError:
                            print(
                                f"----> for nameserver[{i}] '{nameserver}' ({ip.compressed}) found AS record: [{entry}]")
                            # ip_as_db_entries_result[rr.name] = (ip, entry, None)
                            ip_as_results.insert_ip_range_tsv(nameserver, None)
                    except AutonomousSystemNotFoundError:
                        print(f"----> for nameserver[{i}] '{nameserver}' ({ip.compressed}) no AS found.")
                        ip_as_results.insert_ip_as_entry(nameserver, None)
                        ip_as_results.insert_ip_range_tsv(nameserver, None)

        try:
            headless_browser = FirefoxHeadlessWebDriver(PRD)
        except (FilenameNotFoundError, selenium.common.exceptions.WebDriverException) as e:
            print(f"!!! {str(e)} !!!")
            return
        rov_page_scraper = ROVPageScraper(headless_browser)

        reformat = ASResolverResultForROVPageScraping(ip_as_results)
        print("\n\nSTART ROV PAGE SCRAPING")
        for as_number in reformat.results.keys():
            print(f"Loading page for AS{as_number}")
            try:
                rov_page_scraper.load_as_page(as_number)
            except selenium.common.exceptions.WebDriverException as exc:
                print(f"!!! {str(exc)} !!!")
                # non tengo neanche traccia di ciò
                reformat.results[as_number] = None
                continue
            except (TableNotPresentError, ValueError, TableEmptyError, NotROVStateTypeError) as exc:
                print(f"!!! {str(exc)} !!!")
                reformat.results[as_number] = None
                continue
            for nameserver in reformat.results[as_number].keys():
                ip_string = reformat.results[as_number][nameserver].ip_address
                entry_ip_as_db = reformat.results[as_number][nameserver].entry_as_database
                belonging_network_ip_as_db = reformat.results[as_number][nameserver].ip_range_tsv
                try:
                    row = rov_page_scraper.get_network_if_present(ipaddress.ip_address(ip_string))  # non gestisco ValueError perché non può accadere qua
                    reformat.results[as_number][nameserver].insert_rov_entry(row)
                    print(f"--> for '{nameserver}' ({ip_string}), found row: {str(row)}")
                except (TableNotPresentError, TableEmptyError, NetworkNotFoundError) as exc:
                    print(f"!!! {exc.message} !!!")
                    reformat.results[as_number][nameserver].insert_rov_entry(None)
        print("END ROV PAGE SCRAPING")

    def test_1_something(self):
        self.assertEqual(True, True)  # add assertion here

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
