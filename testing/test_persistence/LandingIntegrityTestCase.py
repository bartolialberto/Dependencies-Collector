import unittest
from peewee import DoesNotExist
from entities.resolvers.DnsResolver import DnsResolver
from entities.resolvers.LandingResolver import LandingResolver
from persistence import helper_application_results, helper_web_site_lands, helper_web_server, helper_script_site_lands, \
    helper_script_server


class LandingIntegrityTestCase(unittest.TestCase):
    """
    Test class that checks data integrity of web sites and script sites landing.

    """
    script_sites_results = None
    web_sites_results = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        web_site_list = {
            'google.it/doodles',
            'www.youtube.it/feed/explore'
        }
        script_site_list = {
            'www.youtube.com/s/desktop/d3411c39/jsbin/scheduler.vflset/scheduler.js',
            'www.youtube.com/s/player/18da33ed/player_ias.vflset/it_IT/base.js',
            'www.youtube.com/s/desktop/d3411c39/jsbin/webcomponents-sd.vflset/webcomponents-sd.js',
            'www.youtube.com/s/desktop/d3411c39/jsbin/desktop_polymer.vflset/desktop_polymer.js',
            'www.youtube.com/s/desktop/d3411c39/jsbin/www-i18n-constants-it_IT.vflset/www-i18n-constants.js',
            'www.youtube.com/s/desktop/d3411c39/jsbin/www-tampering.vflset/www-tampering.js',
            'www.youtube.com/s/desktop/d3411c39/jsbin/custom-elements-es5-adapter.vflset/custom-elements-es5-adapter.js',
            'www.google.com/doodles/js/slashdoodles__it.js',
            'www.youtube.com/s/desktop/d3411c39/jsbin/network.vflset/network.js',
            'www.youtube.com/s/desktop/d3411c39/jsbin/web-animations-next-lite.min.vflset/web-animations-next-lite.min.js',
            'ssl.google-analytics.com/ga.js',
            'www.youtube.com/s/player/18da33ed/player_ias.vflset/it_IT/miniplayer.js'
        }
        # ELABORATION
        print(f"START WEB SITE LANDING")
        dns_resolver = DnsResolver(None)
        resolver = LandingResolver(dns_resolver)
        cls.web_sites_results = resolver.resolve_sites(web_site_list)
        print(f"END WEB SITE LANDING")
        print(f"START SCRIPT SITE LANDING")
        resolver = LandingResolver(dns_resolver)
        cls.script_sites_results = resolver.resolve_sites(script_site_list)
        print(f"END SCRIPT SITE LANDING")
        print(f"\nSTART DB INSERTION INTO DATABASE... ", end='')
        helper_application_results.insert_landing_web_sites_results(cls.web_sites_results)
        helper_application_results.insert_landing_script_sites_results(cls.script_sites_results)
        print(f"DONE")

    def test_1_website_has_only_two_website_lands_association_at_most(self):
        print("\n------- [1] START AT MOST 2 WEB_SITE_LANDS_ASSOCIATIONS PER WEBSITE CHECK -------")
        for i, website in enumerate(self.web_sites_results.keys()):
            result = helper_web_site_lands.get_all_from_string_website(website)
            https_result = set(filter(lambda r: r.https, result))
            http_result = set(filter(lambda r: not r.https, result))
            print(f"--> for: {website} there are {len(result)} website_lands rows")
            for wla in result:
                print(f"----> https={wla.https}")
            self.assertLessEqual(len(result), 2)
            self.assertGreaterEqual(len(result), 1)
            self.assertEqual(1, len(https_result))
            self.assertEqual(1, len(http_result))
        print("------- [1] END AT MOST 2 WEB_SITE_LANDS_ASSOCIATIONS PER WEBSITE CHECK -------")

    def test_2_integrity_between_results(self):
        print("\n------- [2] START WEB SITES INTEGRITY CHECK -------")
        for i, website in enumerate(self.web_sites_results.keys()):
            print(f"Result for: {website} through elaboration:")
            if self.web_sites_results[website].https is None:
                elaboration_https_url = 'null'
                elaboration_https = 'null'
            else:
                elaboration_https_url = self.web_sites_results[website].https.url
                elaboration_https = self.web_sites_results[website].https.server
            if self.web_sites_results[website].http is None:
                elaboration_http_url = 'null'
                elaboration_http = 'null'
            else:
                elaboration_http_url = self.web_sites_results[website].http.url
                elaboration_http = self.web_sites_results[website].http.server
            print(f"--> HTTPS landing_http_url from elaboration: {elaboration_https_url}")
            print(f"--> HTTPS landing_url from elaboration: {elaboration_https}")
            print(f"--> HTTP landing_http_url from elaboration: {elaboration_http_url}")
            print(f"--> HTTP landing_url from elaboration: {elaboration_http}")

            print(f"Result for: {website} through database:")
            try:
                wse_https_s = helper_web_server.get_from(website, True, first_only=False)
                if len(wse_https_s) > 1:
                    self.fail(f"ERROR: more than 1 web server found for web site: {website}, on https? {True}")
                else:
                    wse_https = wse_https_s[0]
            except DoesNotExist:
                wse_https = None
            try:
                wse_http_s = helper_web_server.get_from(website, False, first_only=False)
                if len(wse_http_s) > 1:
                    self.fail(f"ERROR: more than 1 web server found for web site: {website}, on https? {False}")
                else:
                    wse_http = wse_http_s[0]
            except DoesNotExist:
                wse_http = None
            if wse_https is None:
                db_https = 'null'
            else:
                db_https = wse_https.name.name
            if wse_http is None:
                db_http = 'null'
            else:
                db_http = wse_http.name.name
            print(f"--> HTTPS landing_url from database: {db_https}")
            print(f"--> HTTP landing_url from database: {db_http}")

            self.assertEqual(elaboration_https, db_https)
            self.assertEqual(elaboration_http, db_http)

            if i != len(self.web_sites_results.keys())-1:
                print()
        print("------- [2] END WEB SITES INTEGRITY CHECK -------")

    def test_3_script_site_has_only_two_script_site_lands_association_at_most(self):
        print("\n------- [3] START AT MOST 2 SCRIPT_SITE_LANDS_ASSOCIATIONS PER WEBSITE CHECK -------")
        for i, script_site in enumerate(self.script_sites_results.keys()):
            result = helper_script_site_lands.get_all_from_script_site_string(script_site)
            https_result = set(filter(lambda r: r.https, result))
            http_result = set(filter(lambda r: not r.https, result))
            print(f"--> for: {script_site} there are {len(result)} script_site_lands rows")
            for wla in result:
                print(f"----> https={wla.https}")
            self.assertLessEqual(len(result), 2)
            self.assertGreaterEqual(len(result), 1)
            self.assertEqual(1, len(https_result))
            self.assertEqual(1, len(http_result))
        print("------- [3] END AT MOST 2 SCRIPT_SITE_LANDS_ASSOCIATIONS PER WEBSITE CHECK -------")

    def test_4_integrity_between_results(self):
        print("\n------- [4] START SCRIPT SITES INTEGRITY CHECK -------")
        for i, script_site in enumerate(self.script_sites_results.keys()):
            print(f"Result for: {script_site} through elaboration:")
            if self.script_sites_results[script_site].https is None:
                elaboration_https_url = 'null'
                elaboration_https = 'null'
            else:
                elaboration_https_url = self.script_sites_results[script_site].https.url
                elaboration_https = self.script_sites_results[script_site].https.server
            if self.script_sites_results[script_site].http is None:
                elaboration_http_url = 'null'
                elaboration_http = 'null'
            else:
                elaboration_http_url = self.script_sites_results[script_site].http.url
                elaboration_http = self.script_sites_results[script_site].http.server
            print(f"--> HTTPS landing_http_url from elaboration: {elaboration_https_url}")
            print(f"--> HTTPS landing_url from elaboration: {elaboration_https}")
            print(f"--> HTTP landing_http_url from elaboration: {elaboration_http_url}")
            print(f"--> HTTP landing_url from elaboration: {elaboration_http}")

            print(f"Result for: {script_site} through database:")
            try:
                wse_https_s = helper_script_server.get_from_string_script_site(script_site, True, first_only=False)
                if len(wse_https_s) > 1:
                    self.fail(f"ERROR: more than 1 script server found for script site: {script_site}, on https? {True}")
                else:
                    wse_https = wse_https_s[0]
            except DoesNotExist:
                wse_https = None
            try:
                wse_http_s = helper_script_server.get_from_string_script_site(script_site, False, first_only=False)
                if len(wse_http_s) > 1:
                    self.fail(f"ERROR: more than 1 script server found for script site: {script_site}, on https? {False}")
                else:
                    wse_http = wse_http_s[0]
            except DoesNotExist:
                wse_http = None
            if wse_https is None:
                db_https = 'null'
            else:
                db_https = wse_https.name.name
            if wse_http is None:
                db_http = 'null'
            else:
                db_http = wse_http.name.name
            print(f"--> HTTPS landing_url from database: {db_https}")
            print(f"--> HTTP landing_url from database: {db_http}")

            self.assertEqual(elaboration_https, db_https)
            self.assertEqual(elaboration_http, db_http)

            if i != len(self.script_sites_results.keys()) - 1:
                print()
        print("------- [4] END SCRIPT SITES INTEGRITY CHECK -------")


if __name__ == '__main__':
    unittest.main()
