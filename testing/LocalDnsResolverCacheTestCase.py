import unittest
from entities.DomainName import DomainName
from entities.LocalDnsResolverCache import LocalDnsResolverCache
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.ReachedMaximumRecursivePathThresholdError import ReachedMaximumRecursivePathThresholdError
from utils import file_utils


class LocalDnsResolverCacheTestCase(unittest.TestCase):
    cache_filename_in_output_folder = None
    cache = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.cache_filename_in_output_folder = 'dns_cache'
        # ELABORATION
        PRD = file_utils.get_project_root_directory()
        cls.cache = LocalDnsResolverCache()
        try:
            cls.cache.load_csv_from_output_folder(cls.cache_filename_in_output_folder, take_snapshot=False, project_root_directory=PRD)
        except FilenameNotFoundError as e:
            print(f"!!! {str(e)} !!!")
            exit(-1)
        print(f"STARTING CACHE WITH {len(cls.cache.cache)} RECORDS")

    def test_1_resolving_path(self):
        print(f"\n------- START TEST 1 -------")
        # PARAMETER
        domain_name = DomainName('www.units.it.')
        type_rr = TypesRR.A
        # TEST
        print(f"Parameter: domain name: {domain_name}")
        try:
            path = self.cache.resolve_path(domain_name, type_rr)
            print(f"{path.stamp()}")
        except (NoAvailablePathError, ReachedMaximumRecursivePathThresholdError) as e:
            self.fail(f"!!! {str(e)} !!!")
        print(f"------- END TEST 1 -------")

    def test_2_close_graph_cycling(self):
        print(f"\n------- START TEST 2 -------")
        start = DomainName('A')
        rr1 = RRecord(start, TypesRR.CNAME, ['B'])
        rr2 = RRecord(DomainName('B'), TypesRR.CNAME, ['C'])
        rr3 = RRecord(DomainName('C'), TypesRR.CNAME, [start.string])
        self.cache.add_entries([rr1, rr2, rr3])
        with self.assertRaises(ReachedMaximumRecursivePathThresholdError):
            path = self.cache.resolve_path(start, TypesRR.A)
            print(f"resolving path didn't raise ReachedMaximumRecursivePathThresholdError...")
        print(f"------- END TEST 2 -------")


if __name__ == '__main__':
    unittest.main()
