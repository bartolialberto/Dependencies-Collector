import copy
import unittest
from pathlib import Path

from entities.enums.TypesRR import TypesRR
from entities.resolvers.DnsResolver import DnsResolver
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoRecordInCacheError import NoRecordInCacheError
from persistence import helper_zone, helper_domain_name, helper_ip_address, helper_access
from persistence.BaseModel import project_root_directory_name


class BlankTestToBeUsedTestCase(unittest.TestCase):
    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == project_root_directory_name:
                return current
            else:
                current = current.parent

    def test_something(self):
        PRD = BlankTestToBeUsedTestCase.get_project_root_folder()
        dns_resolver = DnsResolver(None)
        dns_resolver.cache.load_csv_from_output_folder('cache_from_dns_test', PRD)

        var = 'cdn-auth.digidentity.eu.'

        try:
            zo, cnames = dns_resolver.cache.resolve_zone_object_from_zone_name(var)
            print(f"Zone name resolution path: {zo.stamp_zone_name_resolution_path()}")
        except (NoRecordInCacheError, NoAvailablePathError) as e:
            print(f"!!! {str(e)} !!!")


        print('THE END')


if __name__ == '__main__':
    unittest.main()
