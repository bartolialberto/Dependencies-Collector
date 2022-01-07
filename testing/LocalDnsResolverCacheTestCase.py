import unittest
from pathlib import Path
from entities.LocalDnsResolverCache import LocalDnsResolverCache
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoRecordInCacheError import NoRecordInCacheError


class LocalDnsResolverCacheTestCase(unittest.TestCase):
    domain_name = None
    cache = None

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
        cls.domain_name = 'dns.cnr.it'
        # ELABORATION
        PRD = LocalDnsResolverCacheTestCase.get_project_root_folder()
        cls.cache = LocalDnsResolverCache()
        cls.cache.load_csv_from_output_folder('cache_from_dns_test.csv', PRD)
        print(f"STARTING CACHE WITH {len(cls.cache.cache)} RECORDS, PARAMETER: {cls.domain_name}")
        # EXAMPLES (aliases path)
        # dns.unipd.it. --- alias --> ipdunivx.unipd.it.
        # www.units.it --- alias --> units09.cineca.it.
        # only A resource record: dns.cnr.it
        # only NS resource record: com

    def test_1_forward_path_of_name(self):
        print(f"\nSTART FORWARD PATH RESOLVING")
        try:
            result = self.cache.lookup_forward_path(self.domain_name)
            for i, name in enumerate(result):
                print(f"[{i+1}] = {name}")
        except NoRecordInCacheError:
            print(f"No path for '{self.domain_name}'")
        print(f"END BACKWARD PATH RESOLVING")

    def test_2_backward_path_of_name(self):
        print(f"\nSTART BACKWARD PATH RESOLVING")
        try:
            result = self.cache.lookup_backward_path(self.domain_name)
            for i, name in enumerate(result):
                print(f"[{i+1}] = {name}")
        except NoRecordInCacheError:
            print(f"No path for '{self.domain_name}'")
        print(f"END BACKWARD PATH RESOLVING")

    def test_3_resolving_path(self):
        print(f"\nSTART PATH RESOLVING")
        try:
            result = self.cache.resolve_path_aliases(self.domain_name)
            for i, name in enumerate(result):
                print(f"[{i+1}] = {name}")
        except NoAvailablePathError:
            print(f"No path for '{self.domain_name}'")
        print(f"END PATH RESOLVING")


if __name__ == '__main__':
    unittest.main()
