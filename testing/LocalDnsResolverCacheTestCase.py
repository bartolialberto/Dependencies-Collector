import unittest
from pathlib import Path
from entities.LocalDnsResolverCache import LocalDnsResolverCache
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoRecordInCacheError import NoRecordInCacheError


# EXAMPLES (aliases path)
# dns.unipd.it. --- alias --> ipdunivx.unipd.it. ---> IP ADDRESS
# www.units.it --- alias --> units09.cineca.it. ---> IP ADDRESS
# only A resource record: dns.cnr.it
# only NS resource record: com
# EXAMPLES (zones from nameserver)
# nameserver.cnr.it. nameserver of 5 zones: it., nic.it., cnr.it., ge.cnr.it., ieiit.cnr.it.
# e.dns.br. nameserver of 2 zones: br., dns.br.
# a1-67.akam.net. nameserver of 1 zone: akam.net.
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
        cls.domain_name = 'dns.unipd.it.'
        cls.nameserver = 'nameserver.cnr.it.'
        # ELABORATION
        PRD = LocalDnsResolverCacheTestCase.get_project_root_folder()
        cls.cache = LocalDnsResolverCache()
        cls.cache.load_csv_from_output_folder('cache_from_dns_test.csv', PRD)
        print(f"STARTING CACHE WITH {len(cls.cache.cache)} RECORDS, PARAMETER: {cls.domain_name}")

    def test_1_forward_path_of_name(self):
        print(f"\n------- [1] START FORWARD PATH RESOLVING from domain name = {self.domain_name} -------")
        try:
            result = self.cache.lookup_forward_path(self.domain_name)
            for i, name in enumerate(result):
                print(f"[{i+1}] = {name}")
        except NoRecordInCacheError:
            print(f"No path for '{self.domain_name}'")
        print(f"------- END BACKWARD PATH RESOLVING -------")

    def test_2_backward_path_of_name(self):
        print(f"\n------- [2] START BACKWARD PATH RESOLVING from domain name = {self.domain_name} -------")
        try:
            result = self.cache.lookup_backward_path(self.domain_name)
            for i, name in enumerate(result):
                print(f"[{i+1}] = {name}")
        except NoRecordInCacheError:
            print(f"No path for '{self.domain_name}'")
        print(f"------- [2] END BACKWARD PATH RESOLVING -------")

    def test_3_resolving_path(self):
        print(f"\n------- [3] START PATH RESOLVING from domain name = {self.domain_name} -------")
        try:
            result = self.cache.resolve_path_aliases(self.domain_name)
            for i, name in enumerate(result):
                print(f"[{i+1}] = {name}")
        except NoAvailablePathError:
            print(f"No path for '{self.domain_name}'")
        print(f"------- [3] END PATH RESOLVING -------")

    def test_4_resolving_zones_from_nameserver(self):
        print(f"\n------- [4] START ZONE RESOLVING from nameserver = {self.nameserver} -------")
        try:
            zone_names = self.cache.resolve_zones_from_nameserver(self.nameserver)
            for i, zone_name in enumerate(zone_names):
                print(f"[{i+1}] = {zone_name}")
        except NoRecordInCacheError:
            print(f"No zone found from nameserver '{self.nameserver}'")
        print(f"------- [5] END ZONE RESOLVING -------")


if __name__ == '__main__':
    unittest.main()
