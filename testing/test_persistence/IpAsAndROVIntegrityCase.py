import unittest
from peewee import DoesNotExist
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.DomainName import DomainName
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_application_results, helper_ip_range_tsv, helper_ip_range_rov, helper_ip_address
from utils import file_utils


class IpAsAndROVIntegrityCase(unittest.TestCase):
    """
    Test class that takes a list of domain names in input and executes: DNS resolving, IP-AS resolving and in the end
    ROVPage scraping. Then tests are done to check data integrity of ROVPage scraping (which are linked to the IP-AS
    resolution obviously).

    """
    resolvers = None
    consider_tld = None
    final_results = None
    dns_results = None
    domain_name_list = None


    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_name_list = [
            DomainName('unipd.it'),
            DomainName('google.it'),
            DomainName('youtube.it')
        ]
        cls.consider_tld = True
        # ELABORATION
        PRD = file_utils.get_project_root_directory()
        cls.resolvers = ApplicationResolversWrapper(cls.consider_tld, True, True, PRD, take_snapshot=False)
        cls.dns_results = cls.resolvers.do_dns_resolving(cls.domain_name_list)
        ip_as_results = cls.resolvers.do_ip_as_database_resolving(cls.dns_results, dict(), False)
        rov_scraper_pre_results = ASResolverResultForROVPageScraping(ip_as_results)
        cls.final_results = cls.resolvers.do_rov_page_scraping(rov_scraper_pre_results)
        print("\nInsertion into database... ", end="")
        helper_application_results.insert_dns_result(cls.dns_results)
        helper_application_results.insert_ip_as_and_rov_resolving(cls.final_results)
        print(f"DONE.")

    def test_1_integrity(self):
        print("\n------- START TEST 1 -------")
        for as_number in self.final_results.results.keys():
            print(f"AS{as_number}:")
            if self.final_results.results[as_number] is None:
                print('')
                continue
            for ip_address in self.final_results.results[as_number].keys():
                print(f"--> IP address: {ip_address.exploded}")
                res = self.final_results.results[as_number][ip_address]
                if res is None:
                    elaboration_ip_range_tsv = None
                    elaboration_ip_range_rov = None
                    print(f"----> ip_range_tsv: None")
                    print(f"----> ip_range_rov: None")
                else:
                    elaboration_ip_range_tsv = res.ip_range_tsv.exploded
                    print(f"------> ip_range_tsv: {elaboration_ip_range_tsv}")
                    if res.entry_rov_page is None:
                        elaboration_ip_range_rov = None
                        print(f"------> ip_range_rov: None")
                    else:
                        elaboration_ip_range_rov = res.entry_rov_page.prefix.compressed
                        print(f"------> ip_range_rov: {elaboration_ip_range_rov}")
                # we can't get the name server from the IP address, because there is the case in which name server is an
                # alias of the domain name that resolved such IP address
                try:
                    iae = helper_ip_address.get(ip_address)
                except DoesNotExist:
                    raise
                try:
                    irte = helper_ip_range_tsv.get_of(iae)
                    if irte is None:
                        db_ip_range_tsv = None
                    else:
                        db_ip_range_tsv = irte.compressed_notation
                except NoDisposableRowsError:
                    db_ip_range_tsv = None
                try:
                    irre = helper_ip_range_rov.get_of(iae)
                    if irre is None:
                        db_ip_range_rov = None
                    else:
                        db_ip_range_rov = irre.compressed_notation
                except NoDisposableRowsError:
                    db_ip_range_rov = None
                self.assertEqual(elaboration_ip_range_tsv, db_ip_range_tsv)
                self.assertEqual(elaboration_ip_range_rov, db_ip_range_rov)
        print("------- END TEST 1 -------")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.resolvers.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
