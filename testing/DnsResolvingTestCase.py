import unittest
from pathlib import Path
from typing import List
from entities.DnsResolver import DnsResolver
from entities.Zone import Zone
from entities.error_log.ErrorLogger import ErrorLogger
from exceptions.FilenameNotFoundError import FilenameNotFoundError


class DnsResolvingTestCase(unittest.TestCase):
    PRD = None
    domain_names = None
    dns_resolver = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        # cls.domain_names = ['accounts.google.com', 'login.microsoftonline.com', 'www.facebook.com', 'auth.digidentity.eu', 'clave-dninbrt.seg-social.gob.es', 'pasarela.clave.gob.es']
        # cls.domain_names = ['unipd.it', 'units.it', 'dei.unipd.it', 'ocsp.digicert.com', 'lorenzo.fabbio@unipd.it', 'studente110847@dei.unipd.it']
        # cls.domain_names = ['unipd.it', 'dei.unipd.it']
        cls.domain_names = ['ocsp.digicert.com']
        # cls.domain_names = ['modor.verisign.net']
        # elaboration
        cls.PRD = DnsResolvingTestCase.get_project_root_folder()
        cls.dns_resolver = DnsResolver()
        try:
            cls.dns_resolver.cache.load_csv_from_output_folder(filename='cache_from_dns_test.csv', project_root_directory=cls.PRD)
        except FilenameNotFoundError:
            pass
        cls.dns_resolver.cache.cache.clear()
        cls.results, cls.error_logs = DnsResolvingTestCase.dns_resolving(cls.dns_resolver, cls.domain_names)

    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == 'LavoroTesi':
                return current
            else:
                current = current.parent

    @staticmethod
    def dns_resolving(dns_resolver: DnsResolver, domain_names: List[str]):
        print("START DNS DEPENDENCIES RESOLVER")
        dns_results, error_logs = dns_resolver.resolve_multiple_domains_dependencies(domain_names)
        print("END DNS DEPENDENCIES RESOLVER")
        return dns_results, error_logs

    @staticmethod
    def print_differences(reference_list: List[Zone], _list: List[Zone]):
        less = list()
        more = list()
        check = list()
        for elem in reference_list:
            if elem in _list and elem not in check:
                check.append(elem)
            elif elem in _list and elem in check:
                print(f"more[{len(more)+1}]: {elem}")
                more.append(elem)
            else:
                print(f"less[{len(less)+1}]: {elem}")
                less.append(elem)

    def test_results(self):
        self.dns_resolver.cache.write_to_csv_in_output_folder(filename="cache_from_dns_test", project_root_directory=self.PRD)
        logger = ErrorLogger()
        for log in self.error_logs:
            logger.add_entry(log)
        logger.write_to_csv_in_output_folder(filename='error_logs_from_test', project_root_directory=self.PRD)

    def test_results_equality_from_cache(self):
        self.new_results, self.new_error_logs = DnsResolvingTestCase.dns_resolving(self.dns_resolver, self.domain_names)
        for domain_name in self.domain_names:
            print(f"print_diff 1 *******************")
            DnsResolvingTestCase.print_differences(self.results[domain_name], self.new_results[domain_name])
            print(f"print_diff 2 *******************")
            DnsResolvingTestCase.print_differences(self.new_results[domain_name], self.results[domain_name])
            self.assertEqual(len(self.results[domain_name]), len(self.new_results[domain_name]))
            self.assertListEqual(self.results[domain_name], self.new_results[domain_name])

    def test_there_are_duplicates_in_results(self):
        duplicates = list()
        for i, rr in enumerate(self.results):
            for j, comp in enumerate(self.results):
                if i != j and rr == comp:
                    duplicates.append(rr)
        if len(duplicates) != 0:
            print(f"\n\nPrinting results duplicates (will be doubled):")
            for i, elem in enumerate(duplicates):
                print(f"duplicates[{i+1}] = {str(elem)}")
        # self.assertCountEqual(self.dns_resolver.cache.cache, keep_track_list)
        self.assertEqual(0, len(duplicates))

    def test_there_are_duplicates_in_cache(self):
        duplicates = list()
        for i, rr in enumerate(self.dns_resolver.cache.cache):
            for j, comp in enumerate(self.dns_resolver.cache.cache):
                if i != j and rr == comp:
                    duplicates.append(rr)
        if len(duplicates) != 0:
            print(f"\n\nPrinting cache duplicates (will be doubled):")
            for i, elem in enumerate(duplicates):
                print(f"duplicates[{i+1}] = {str(elem)}")
        # self.assertCountEqual(self.dns_resolver.cache.cache, keep_track_list)
        self.assertEqual(0, len(duplicates))


if __name__ == '__main__':
    unittest.main()
