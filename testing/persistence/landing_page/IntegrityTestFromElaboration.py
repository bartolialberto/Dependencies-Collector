import unittest
from typing import List
import requests
from peewee import DoesNotExist
from persistence import helper_landing_page, helper_domain_name
from utils import requests_utils


class IntegrityTestFromElaboration(unittest.TestCase):
    """
    Test class

    """
    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        # cls.domain_name_list = ['unipd.it', 'google.it', 'youtube.it']
        # cls.domain_name_list = ['www.units.it', 'unipd.it']
        cls.domain_name_list = ['google.de', 'youtube.de', 'facebook.it', 'accounts.google.com', 'login.microsoftonline.com']

    @staticmethod
    def landing_page_resolving(domain_names: List[str]):
        print("START LANDING PAGE RESOLVER")
        landing_page_results = dict()
        for domain_name in domain_names:
            print(f"\nTrying to connect to domain '{domain_name}' via HTTPS:")
            try:
                (landing_url, redirection_path, hsts) = requests_utils.resolve_landing_page(domain_name, as_https=True)
                print(f"Landing url: {landing_url}")
                print(f"HTTP Strict Transport Security: {hsts}")
                print(f"Redirection path:")
                for index, url in enumerate(redirection_path):
                    print(f"[{index + 1}/{len(redirection_path)}]: {url}")
                landing_page_results[domain_name] = (landing_url, redirection_path, hsts)
            except Exception as exc:  # sono tante!
                print(f"!!! {str(exc)} !!!")
        print("END LANDING PAGE RESOLVER")
        return landing_page_results

    def setUp(self) -> None:
        self.results = IntegrityTestFromElaboration.landing_page_resolving(self.domain_name_list)
        helper_landing_page.multiple_inserts(self.results)
        #
        # helper_landing_page.test()

    def test_integrity(self):
        print("\nSTART INTEGRITY CHECK")
        for i, domain_name in enumerate(self.results.keys()):
            landing_url = self.results[domain_name][0]
            redirection_path = self.results[domain_name][1]
            hsts = self.results[domain_name][2]
            try:
                landing_url_db, redirection_path_db, hsts_db = helper_landing_page.get_from_domain_name(domain_name) #.get_from_url(landing_url)
            except DoesNotExist:
                print(f"!!! DoesNotExist raised from url: {landing_url} !!!")
                exit(1)
            print(f"Result for '{domain_name}' through elaboration:")
            print(f"--> landing_url from elaboration: {landing_url}")
            print(f"--> redirection_path from elaboration: {redirection_path}")
            print(f"--> hsts from elaboration: {hsts}")
            print(f"Result for '{domain_name}' through database:")
            print(f"--> landing_url from database: {landing_url_db}")
            print(f"--> redirection_path from database: {redirection_path_db}")
            print(f"--> hsts from database: {hsts_db}")
            self.assertEqual(landing_url, landing_url_db)
            self.assertEqual(len(redirection_path), len(redirection_path_db))     # TODO: implementare l'ordine nel DB di redirection path... Poi usare assertListEqual
            self.assertEqual(hsts, hsts_db)
            print("")
        print("END INTEGRITY CHECK")


if __name__ == '__main__':
    unittest.main()
