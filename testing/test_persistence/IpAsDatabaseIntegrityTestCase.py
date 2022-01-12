import ipaddress
import unittest
from pathlib import Path
from typing import List
from entities.DnsResolver import DnsResolver
from entities.IpAsDatabase import IpAsDatabase
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from persistence import helper_domain_name, helper_entry_ip_as_database
from utils import file_utils, requests_utils


class IpAsDatabaseIntegrityTestCase(unittest.TestCase):
    """
    Test class
    """
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
        cls.domain_name_list = ['unipd.it', 'google.it', 'youtube.it']
        cls.use_cache = False

    @staticmethod
    def set_up_dns_resolver(use_cache: bool, PRD: Path) -> DnsResolver:
        dns_resolver = DnsResolver()
        if use_cache:
            try:
                dns_resolver.cache.load_csv_from_output_folder(PRD)
            except (ValueError, FilenameNotFoundError, OSError) as exc:
                print(f"!!! {str(exc)} !!!")
                exit(1)
        return dns_resolver

    @staticmethod
    def dns_resolving(dns_resolver: DnsResolver, domain_names: List[str]) -> dict:
        print("START DNS DEPENDENCIES RESOLVER")
        dns_results = dns_resolver.resolve_multiple_domains_dependencies(domain_names)
        print("END DNS DEPENDENCIES RESOLVER")
        return dns_results

    @staticmethod
    def set_up_database_resolver(PRD: Path) -> IpAsDatabase:
        tsv_db_is_updated = file_utils.is_tsv_database_updated(project_root_directory=PRD)
        if tsv_db_is_updated:
            print("> .tsv database file is updated.")
        else:
            print("> Latest .tsv database (~25 MB) is downloading and extracting... ", end='')
            requests_utils.download_latest_tsv_database(project_root_directory=PRD)
            print("DONE.")
        try:
            ip_as_database = IpAsDatabase(project_root_directory=PRD)
        except (FileWithExtensionNotFoundError, OSError) as e:
            print(f"!!! {str(e)} !!!")
            exit(1)
        return ip_as_database

    @staticmethod
    def ip_as_database_resolving(ip_as_database: IpAsDatabase, dns_results: dict):
        print("START IP-AS RESOLVER")
        ip_as_db_entries_result = dict()
        for index_domain, domain in enumerate(dns_results.keys()):
            print(f"Handling domain[{index_domain}] '{domain}'")
            for index_zone, zone in enumerate(dns_results[domain]):
                print(f"--> Handling zone[{index_zone}] '{zone.url}'")
                for index_rr, rr in enumerate(zone.zone_dependencies_per_nameserver):
                    try:
                        ip = ipaddress.IPv4Address(rr.get_first_value())
                        entry = ip_as_database.resolve_range(ip)
                        try:
                            belonging_network_ip_as_db, networks = entry.get_network_of_ip(ip)
                            print(
                                f"----> for nameserver[{index_rr}] '{rr.url}' ({rr.get_first_value()}) found AS{str(entry.as_number)}: [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. Belonging network: {belonging_network_ip_as_db.compressed}")
                            ip_as_db_entries_result[rr.url] = (rr.get_first_value(), entry, belonging_network_ip_as_db)
                        except ValueError as exc:
                            print(
                                f"----> for nameserver[{index_rr}] '{rr.url}' ({rr.get_first_value()}) found AS record: [{entry}]")
                            ip_as_db_entries_result[rr.url] = (rr.get_first_value(), entry, None)
                    except AutonomousSystemNotFoundError as exc:
                        print(f"----> for nameserver[{index_rr}] '{rr.url}' ({rr.get_first_value()}) no AS found.")
                        ip_as_db_entries_result[rr.url] = (ip, None, None)  # TODO: tenerne traccia in qualche modo
        print("END IP-AS RESOLVER")
        return ip_as_db_entries_result

    def setUp(self) -> None:
        self.PRD = IntegrityTestFromElaboration.get_project_root_folder()
        self.dns_resolver = IntegrityTestFromElaboration.set_up_dns_resolver(self.use_cache, self.PRD)
        self.dns_results = IntegrityTestFromElaboration.dns_resolving(self.dns_resolver, self.domain_name_list)
        helper_domain_name.multiple_inserts(self.dns_results)
        self.ip_as_database_resolver = IntegrityTestFromElaboration.set_up_database_resolver(self.PRD)
        self.results = IntegrityTestFromElaboration.ip_as_database_resolving(self.ip_as_database_resolver, self.dns_results)
        helper_entry_ip_as_database.multiple_inserts(self.results, True)

    def test_integrity(self):
        print("\nSTART INTEGRITY CHECK")
        for i, nameserver in enumerate(self.results.keys()):
            ip_string = self.results[nameserver][0]
            entry = self.results[nameserver][1]
            belonging_network = self.results[nameserver][2]
            ip_string_db, entry_db, belonging_network_db = helper_entry_ip_as_database.get_with_relation_too_from_nameserver(nameserver)
            print(f"Results of '{nameserver}' from elaboration:")
            print(f"--> ip_string:{ip_string}")
            print(f"--> entry:{str(entry)}")
            print(f"--> belonging_network:{belonging_network}")
            print(f"Results of '{nameserver}' from database:")
            print(f"--> ip_string:{ip_string_db}")
            print(f"--> entry:{str(entry_db)}")
            print(f"--> belonging_network:{belonging_network_db}")
            self.assertEqual(ip_string, ip_string_db)
            self.assertEqual(entry, entry_db)
            self.assertEqual(belonging_network, belonging_network_db)
            print(f"")
        print("END INTEGRITY CHECK")


if __name__ == '__main__':
    unittest.main()
