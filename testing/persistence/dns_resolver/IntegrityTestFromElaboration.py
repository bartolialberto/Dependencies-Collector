import unittest
from pathlib import Path
from typing import List
from entities.DnsResolver import DnsResolver
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from persistence import helper_domain_name


class IntegrityTestFromElaboration(unittest.TestCase):
    """
    Test class that takes a list of domain names and then executes the DNS resolving.
    Finally checks the integrity of the zone dependencies found with what was saved and retrieved from the database.

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
    def set_up_resolver(use_cache: bool, project_root_directory: Path):
        dns_resolver = DnsResolver()
        if use_cache:
            try:
                dns_resolver.cache.load_csv_from_output_folder(project_root_directory=project_root_directory)
            except (ValueError, FilenameNotFoundError, OSError) as exc:
                print(f"!!! {str(exc)} !!!")
                exit(1)
        return dns_resolver

    @staticmethod
    def dns_resolving(dns_resolver: DnsResolver, domain_names: List[str]):
        print("START DNS DEPENDENCIES RESOLVER")
        dns_results = dns_resolver.search_multiple_domains_dependencies(domain_names)
        print("END DNS DEPENDENCIES RESOLVER")
        return dns_results

    def setUp(self) -> None:
        self.PRD = IntegrityTestFromElaboration.get_project_root_folder()
        self.dns_resolver = IntegrityTestFromElaboration.set_up_resolver(self.use_cache, self.PRD)
        self.results = IntegrityTestFromElaboration.dns_resolving(self.dns_resolver, self.domain_name_list)
        helper_domain_name.multiple_inserts(self.results)

    def test_integrity(self):
        print("\nSTART INTEGRITY CHECK")
        for i, domain_name in enumerate(self.results.keys()):
            list_zones = helper_domain_name.get_zone_dependencies(domain_name)
            self.assertEqual(len(self.results[domain_name]), len(list_zones))
            print(f"Tot zone dependencies for '{domain_name}':")
            print(f"--> number of zone dependencies found from elaboration: {len(self.results[domain_name])}")
            for j, zone in enumerate(self.results[domain_name]):
                print(f"----> number of nameservers of zone[{j+1}/{len(self.results[domain_name])}] '{zone.name}' from elaboration is: {len(zone.nameservers)}")
            print(f"--> number of zone dependencies found in the database: {len(list_zones)}")
            for j, zone in enumerate(list_zones):
                print(f"----> number of nameservers of zone[{j+1}/{len(list_zones)}] '{zone.name}' from database is: {len(zone.nameservers)}")
            # integrity test
            for z in self.results[domain_name]:
                try:
                    list_zones.remove(z)   # needs an overwritten __eq__ method in Zone class
                except ValueError:
                    print(f"!!! There's a zone dependency from elaboration not present in the database: {str(z)} !!!")
            # for every zone dependency of the elaboration, it is removed from the list (of zone dependencies) retrieved
            # from the database. So in the end, if everything is correct, the list should be empty.
            self.assertEqual(0, len(list_zones))
            print("")
        print("END INTEGRITY CHECK")


if __name__ == '__main__':
    unittest.main()
