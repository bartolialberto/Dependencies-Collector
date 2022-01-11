import unittest
from peewee import DoesNotExist
from entities.LandingResolver import LandingResolver
from persistence import helper_application_results, helper_web_site_lands, helper_web_server
from utils import url_utils


class LandingIntegrityTestCase(unittest.TestCase):
    """
    Test class

    """
    results = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        persist_errors = True
        website_list = {
            'google.de',
            'youtube.de',
            'facebook.it',
            'accounts.google.com',
            'login.microsoftonline.com',
            'auth.digidentity.eu',
            'clave-dninbrt.seg-social.gob.es',
            'youtube.it',
            'darklyrics.com'
        }
        # ELABORATION
        print(f"START LANDING")
        resolver = LandingResolver()
        cls.results, error_logs = resolver.resolve_web_sites(website_list)
        print(f"END LANDING")
        print(f"\nSTART DB INSERTION INTO DATABASE... ", end='')
        helper_application_results.insert_landing_websites_results(cls.results, persist_errors=persist_errors)
        print(f"DONE")

    def test_1_website_has_only_two_website_lands_association_at_most(self):
        print("\nSTART AT MOST 2 WEB_SITE_LANDS_ASSOCIATIONS PER WEBSITE CHECK")
        for i, website in enumerate(self.results.keys()):
            result = helper_web_site_lands.get_all_from_string_website(website)
            print(f"--> for '{website}' there are {len(result)} website_lands rows")
            for i, wla in enumerate(result):
                print(f"----> [{i+1}] https={wla.https}")
            self.assertLessEqual(len(result), 2)
            self.assertGreaterEqual(len(result), 1)
        print("END AT MOST 2 WEB_SITE_LANDS_ASSOCIATIONS PER WEBSITE CHECK")

    def test_2_integrity_between_results(self):
        print("\nSTART INTEGRITY CHECK")
        for i, website in enumerate(self.results.keys()):
            print(f"Result for '{website}' through elaboration:")
            if self.results[website][0] is None:
                elaboration_https_url = 'null'
                elaboration_https = 'null'
            else:
                elaboration_https_url = self.results[website][0].url
                elaboration_https = url_utils.deduct_second_component(self.results[website][0].url)
            if self.results[website][1] is None:
                elaboration_http_url = 'null'
                elaboration_http = 'null'
            else:
                elaboration_http_url = self.results[website][1].url
                elaboration_http = url_utils.deduct_second_component(self.results[website][1].url)
            print(f"--> HTTPS landing_http_url from elaboration: {elaboration_https_url}")
            print(f"--> HTTPS landing_url from elaboration: {elaboration_https}")
            print(f"--> HTTP landing_http_url from elaboration: {elaboration_http_url}")
            print(f"--> HTTP landing_url from elaboration: {elaboration_http}")

            print(f"Result for '{website}' through database:")
            try:
                wse_https = helper_web_server.get_first_from_string_website_and_https_flag(website, True)
            except DoesNotExist:
                wse_https = None
            try:
                wse_http = helper_web_server.get_first_from_string_website_and_https_flag(website, False)
            except DoesNotExist:
                wse_http = None
            if wse_https is None:
                db_https = 'null'
            else:
                db_https = wse_https.url.string
            if wse_http is None:
                db_http = 'null'
            else:
                db_http = wse_http.url.string
            print(f"--> HTTPS landing_url from database: {db_https}")
            print(f"--> HTTP landing_url from database: {db_http}")

            self.assertEqual(elaboration_https, db_https)
            self.assertEqual(elaboration_http, db_http)

            if i != len(self.results.keys())-1:
                print()
        print("END INTEGRITY CHECK")


if __name__ == '__main__':
    unittest.main()
