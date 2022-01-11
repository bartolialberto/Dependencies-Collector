import unittest
from peewee import DoesNotExist
from entities.LandingResolver import LandingResolver
from persistence import helper_web_server, helper_web_site, helper_application_results


class WebServerQueryTestCase(unittest.TestCase):
    website = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.website = 'https://consent.google.de/ml?continue=https://www.google.de/&gl=IT&m=0&pc=shp&hl=it&src=1'
        persist_errors = True
        # ELABORATION
        resolver = LandingResolver()
        try:
            https_result, http_result = resolver.resolve_web_site(cls.website)
        except Exception as e:
            print(f"ERROR: {str(e)}")
            exit(0)
        results = dict()
        results[cls.website] = (https_result, http_result)
        helper_application_results.insert_landing_websites_results(results)
        #
        cls.wse = helper_web_site.get(cls.website)

    def test_1_getting_all_webserver(self):
        print(f"WebServer found for website '{self.website}'")
        try:
            wses = helper_web_server.get_from_string_website(self.website)
        except DoesNotExist:
            print(f"NO WEBSERVER FOR WEBSITE: {self.website} ...")
            exit(0)
        for i, wse in enumerate(wses):
            print(f"[{i+1}/{len(wses)}]: https={wse}, url={wse.url}")
            # print(f"[{i+1}/{len(wses)}]: https={wse[1]}, url={wse[0].url}")   # and the https flag?


if __name__ == '__main__':
    unittest.main()
