import unittest
from pathlib import Path
from entities.LocalDnsResolverCache import LocalDnsResolverCache
from exceptions.FilenameNotFoundError import FilenameNotFoundError
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
    cache_filename_in_output_folder = None
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
        cls.cache_filename_in_output_folder = 'dns_cache'
        # ELABORATION
        PRD = LocalDnsResolverCacheTestCase.get_project_root_folder()
        cls.cache = LocalDnsResolverCache()
        try:
            cls.cache.load_csv_from_output_folder(cls.cache_filename_in_output_folder+'.csv', take_snapshot=False, project_root_directory=PRD)
        except FilenameNotFoundError as e:
            print(f"!!! {str(e)} !!!")
            exit(-1)
        print(f"STARTING CACHE WITH {len(cls.cache.cache)} RECORDS")

    def test_1_resolving_path(self):
        # PARAMETER
        domain_name = 'www.units.it.'
        as_string = True
        # TEST
        print(f"\n------- [1] START PATH RESOLVING -------")
        print(f"Parameter: domain name: {domain_name}")
        try:
            rr_a, aliases = self.cache.resolve_path(domain_name, TypesRR.A, as_string=as_string)
            print(f"as_string is set to: {as_string}")
            print(f"Aliases found through access path:")
            if as_string:
                for i, name in enumerate(aliases):
                    print(f"alias[{i+1}] = {name}")
            else:
                for i, rr in enumerate(aliases):
                    print(f"alias[{i + 1}] = (name={rr.name}, first_value={rr.get_first_value()})")
            print(f"Resolved RR:")
            print(f"(name={rr_a.name}, values={rr_a.values})")
        except NoAvailablePathError:
            print(f"No path for '{domain_name}'")
        print(f"------- [1] END PATH RESOLVING -------")

    def test_2_resolving_zones_from_nameserver(self):
        print(f"\n------- [2] START ZONE RESOLVING from nameserver -------")
        # PARAMETER
        nameserver = 'nameserver.cnr.it.'
        # TEST
        print(f"Parameter: name server: {nameserver}")
        try:
            zone_names = self.cache.resolve_zones_from_nameserver(nameserver)
            for i, zone_name in enumerate(zone_names):
                print(f"[{i+1}] = {zone_name}")
        except NoRecordInCacheError:
            print(f"No zone found from nameserver '{nameserver}'")
        print(f"------- [2] END ZONE RESOLVING -------")

    def test_3_resolving_nameserver_from_zone_object(self):
        print(f"\n------- [3] START NAMESERVER FROM ZONE NAME TEST -------")
        # PARAMETER
        zone_name = 'dei.unipd.it'
        # TEST
        print(f"Parameter: zone name = {zone_name}")
        try:
            zone, rr_cnames = self.cache.resolve_zone_object_from_zone_name(zone_name)
            if len(rr_cnames) == 0:
                pass
            else:
                print(f"Zone name resolution path: {zone.stamp_zone_name_resolution_path()}")
            for i, nameserver in enumerate(zone.nameservers):
                rr = zone.resolve_name_server_access_path(nameserver)
                print(f"for nameserver[{i+1}]: {nameserver}\tresolved = {rr.values}")
        except (NoAvailablePathError, NoRecordInCacheError) as e:
            print(f"!!! {str(e)} !!!")
        print(f"------- [3] END NAMESERVER FROM ZONE NAME TEST -------")


if __name__ == '__main__':
    unittest.main()
