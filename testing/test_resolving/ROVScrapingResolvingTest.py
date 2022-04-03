import unittest
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.DomainName import DomainName
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from utils import file_utils


class ROVScrapingResolvingTestCase(unittest.TestCase):
    domain_names = None
    resolvers = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_names = [
            DomainName('google.it')
        ]
        consider_tld = True
        # ELABORATION
        execute_script_resolving = False
        execute_rov_scraping = True
        take_snapshot = False
        PRD = file_utils.get_project_root_directory()
        cls.resolvers = ApplicationResolversWrapper(consider_tld, execute_script_resolving, execute_rov_scraping, PRD, take_snapshot)
        dns_results = cls.resolvers.do_dns_resolving(cls.domain_names)
        ip_as_results = cls.resolvers.do_ip_as_database_resolving(dns_results, dict(), False)
        reformat = ASResolverResultForROVPageScraping(ip_as_results)
        cls.final_results = cls.resolvers.do_rov_page_scraping(reformat)

    def test_01_unresolved_addresses(self):
        print(f"\n------- [1] START UNRESOLVED ADDRESSES TEST -------")
        for as_number in self.final_results.results.keys():
            for ip_address in self.final_results.results[as_number].keys():
                if self.final_results.results[as_number][ip_address].entry_rov_page is None:
                    print(f"AS{as_number} --> {ip_address} NO ROV RESULTS")
        print(f"------- [1] END UNRESOLVED ADDRESSES TEST -------")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.resolvers.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
