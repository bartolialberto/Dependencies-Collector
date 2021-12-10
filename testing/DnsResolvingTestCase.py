import unittest
from pathlib import Path
from typing import List
from entities.DnsResolver import DnsResolver
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from entities.error_log.ErrorLogger import ErrorLogger


class DnsResolvingTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dns_resolver = DnsResolver()
        cls.domain_names = ['unipd.it', 'units.it', 'dei.unipd.it', 'ocsp.digicert.com']
        # cls.domain_names = ['unipd.it', 'dei.unipd.it']

    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == 'LavoroTesi':
                return current
            else:
                current = current.parent

    @staticmethod
    def dns_resolving_OLD(dns_resolver: DnsResolver, domain_names: List[str]):
        print("START OLD DNS DEPENDENCIES RESOLVER")
        old_dns_results = dns_resolver.search_multiple_domains_dependencies_OLD(domain_names)
        print("END OLD DNS DEPENDENCIES RESOLVER")
        return old_dns_results

    @staticmethod
    def dns_resolving(dns_resolver: DnsResolver, domain_names: List[str]):
        print("\n\nSTART DNS DEPENDENCIES RESOLVER")
        dns_results, error_logs = dns_resolver.search_multiple_domains_dependencies(domain_names)
        print("END DNS DEPENDENCIES RESOLVER")
        return dns_results, error_logs

    @staticmethod
    def copy_list_without_an_element(_list: list, element):
        result = list()
        for e in _list:
            if e != element:
                result.append(e)
            else:
                pass
        return result

    def setUp(self) -> None:
        self.PRD = DnsResolvingTestCase.get_project_root_folder()
        self.dns_resolver.cache.clear()
        self.old_results = DnsResolvingTestCase.dns_resolving_OLD(self.dns_resolver, self.domain_names)
        self.dns_resolver.cache.clear()
        self.results, self.error_logs = DnsResolvingTestCase.dns_resolving(self.dns_resolver, self.domain_names)

    def test_results(self):
        self.assertCountEqual(self.old_results, self.results)
        self.assertSetEqual(set(self.old_results), set(self.results))
        self.dns_resolver.cache.write_to_csv_in_output_folder(project_root_directory=self.PRD)
        logger = ErrorLogger()
        for log in self.error_logs:
            logger.add_entry(log)
        logger.write_to_csv_in_output_folder('from_dns_test', self.PRD)

        # are there duplicates in cache?
        duplicates = list()
        for i, rr in enumerate(self.dns_resolver.cache.cache):
            for j, comp in enumerate(self.dns_resolver.cache.cache):
                if i != j and rr == comp:
                    duplicates.append(rr)
        if len(duplicates) != 0:
            print(f"\n\nPrinting duplicates (will be doubled):")
            for i, elem in enumerate(duplicates):
                print(f"duplicates[{i+1}] = {str(elem)}")
        # self.assertCountEqual(self.dns_resolver.cache.cache, keep_track_list)
        self.assertEqual(0, len(duplicates))


if __name__ == '__main__':
    unittest.main()
