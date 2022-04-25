import unittest
from entities.Url import Url
from entities.resolvers.DnsResolver import DnsResolver
from entities.resolvers.LandingResolver import LandingResolver
from persistence import helper_application_results, helper_web_site_lands, helper_script_site_lands, helper_web_site,\
    helper_script_site


class LandingIntegrityCase(unittest.TestCase):
    """
    DEFINITIVE TEST
    Test class that checks data integrity of web sites and script sites landing.

    """
    script_sites_results = None
    web_sites_results = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        web_sites = {
            Url('google.it/doodles'),
            Url('www.youtube.it/feed/explore'),
            Url('www.darklyrics.com')
        }
        script_sites = {
            Url('www.youtube.com/s/desktop/d3411c39/jsbin/scheduler.vflset/scheduler.js'),
            Url('www.youtube.com/s/player/18da33ed/player_ias.vflset/it_IT/base.js'),
            Url('www.youtube.com/s/desktop/d3411c39/jsbin/webcomponents-sd.vflset/webcomponents-sd.js'),
            Url('www.youtube.com/s/desktop/d3411c39/jsbin/desktop_polymer.vflset/desktop_polymer.js'),
            Url('www.youtube.com/s/desktop/d3411c39/jsbin/www-i18n-constants-it_IT.vflset/www-i18n-constants.js'),
            Url('www.youtube.com/s/desktop/d3411c39/jsbin/www-tampering.vflset/www-tampering.js'),
            Url('www.youtube.com/s/desktop/d3411c39/jsbin/custom-elements-es5-adapter.vflset/custom-elements-es5-adapter.js'),
            Url('www.google.com/doodles/js/slashdoodles__it.js'),
            Url('www.youtube.com/s/desktop/d3411c39/jsbin/network.vflset/network.js'),
            Url('www.youtube.com/s/desktop/d3411c39/jsbin/web-animations-next-lite.min.vflset/web-animations-next-lite.min.js'),
            Url('ssl.google-analytics.com/ga.js'),
            Url('www.youtube.com/s/player/18da33ed/player_ias.vflset/it_IT/miniplayer.js')
        }
        # ELABORATION
        print(f"START WEB SITE LANDING")
        dns_resolver = DnsResolver(True)
        resolver = LandingResolver(dns_resolver)
        cls.web_sites_results = resolver.resolve_sites(web_sites)
        print(f"END WEB SITE LANDING")
        print(f"START SCRIPT SITE LANDING")
        resolver = LandingResolver(dns_resolver)
        cls.script_sites_results = resolver.resolve_sites(script_sites)
        print(f"END SCRIPT SITE LANDING")
        print(f"\nSTART DB INSERTION INTO DATABASE... ", end='')
        helper_application_results.insert_landing_web_sites_results(cls.web_sites_results)
        helper_application_results.insert_landing_script_sites_results(cls.script_sites_results)
        print(f"DONE")

    def test_1_website_has_only_two_website_lands_association_at_most(self):
        print("\n------- [1] START AT MOST 2 WEB_SITE_LANDS_ASSOCIATIONS PER WEBSITE CHECK -------")
        for i, website in enumerate(self.web_sites_results.keys()):
            wse = helper_web_site.get(website)
            wslas = helper_web_site_lands.test_getting_unlimited_association_from(wse)
            https_wslas = set()
            http_wslas = set()
            print(f"--> for: {website} there are {len(wslas)} website_lands rows")
            for wla in wslas:
                print(f"----> starting_https={wla.starting_https}")
                if wla.starting_https:
                    https_wslas.add(wla)
                else:
                    http_wslas.add(wla)
            self.assertEqual(2, len(wslas))
            self.assertEqual(1, len(https_wslas))
            self.assertEqual(1, len(http_wslas))
        print("------- [1] END AT MOST 2 WEB_SITE_LANDS_ASSOCIATIONS PER WEBSITE CHECK -------")

    def test_2_integrity_between_results(self):
        print("\n------- [2] START WEB SITES INTEGRITY CHECK -------")
        for i, website in enumerate(self.web_sites_results.keys()):
            print(f"Result for: {website} through elaboration:")
            if self.web_sites_results[website].https is None:
                elaboration_https_landing_url = None
            else:
                elaboration_https_landing_url = self.web_sites_results[website].https.url.string
            if self.web_sites_results[website].http is None:
                elaboration_http_landing_url = None
            else:
                elaboration_http_landing_url = self.web_sites_results[website].http.url.string
            print(f"--> from HTTPS starting scheme: landing url={elaboration_https_landing_url}")
            print(f"--> from HTTP starting scheme: landing url={elaboration_http_landing_url}")

            print(f"Result for: {website} through database:")
            wse = helper_web_site.get(website)
            is_https = True
            wsla = helper_web_site_lands.get_from_web_site_and_starting_scheme(wse, is_https)
            db_https_landing_url = wsla.landing_url
            is_https = False
            wsla = helper_web_site_lands.get_from_web_site_and_starting_scheme(wse, is_https)
            db_http_landing_url = wsla.landing_url
            print(f"--> from HTTPS starting scheme: landing url={db_https_landing_url}")
            print(f"--> from HTTP starting scheme: landing url={db_http_landing_url}")

            self.assertEqual(elaboration_https_landing_url, db_https_landing_url)
            self.assertEqual(elaboration_http_landing_url, db_http_landing_url)
        print("------- [2] END WEB SITES INTEGRITY CHECK -------")

    def test_3_script_site_has_only_two_script_site_lands_association_at_most(self):
        print("\n------- [3] START AT MOST 2 SCRIPT_SITE_LANDS_ASSOCIATIONS PER WEBSITE CHECK -------")
        for i, script_site in enumerate(self.script_sites_results.keys()):
            sse = helper_script_site.get(script_site)
            sslas = helper_script_site_lands.test_getting_unlimited_association_from(sse)
            if len(sslas) == 1:
                ssla = sslas.pop()
                if ssla.script_server is not None:
                    raise ValueError
                else:
                    continue
            https_sslas = set()
            http_sslas = set()
            print(f"--> for: {script_site} there are {len(sslas)} script_site_lands rows")
            for ssla in sslas:
                print(f"----> starting_https={ssla.starting_https}")
                if ssla.starting_https:
                    https_sslas.add(ssla)
                else:
                    http_sslas.add(ssla)
            self.assertLessEqual(len(sslas), 2)
            self.assertGreaterEqual(len(sslas), 1)
            self.assertEqual(1, len(https_sslas))
            self.assertEqual(1, len(http_sslas))
        print("------- [3] END AT MOST 2 SCRIPT_SITE_LANDS_ASSOCIATIONS PER WEBSITE CHECK -------")

    def test_4_integrity_between_results(self):
        print("\n------- [4] START SCRIPT SITES INTEGRITY CHECK -------")
        for i, script_site in enumerate(self.script_sites_results.keys()):
            print(f"Result for: {script_site} through elaboration:")
            if self.script_sites_results[script_site].https is None:
                elaboration_https_landing_url = None
            else:
                elaboration_https_landing_url = self.script_sites_results[script_site].https.url.string
            if self.script_sites_results[script_site].http is None:
                elaboration_http_landing_url = None
            else:
                elaboration_http_landing_url = self.script_sites_results[script_site].http.url.string
            print(f"--> from HTTPS starting scheme: landing url={elaboration_https_landing_url}")
            print(f"--> from HTTP starting scheme: landing url={elaboration_http_landing_url}")

            print(f"Result for: {script_site} through database:")
            sse = helper_script_site.get(script_site)
            is_https = True
            ssla = helper_script_site_lands.get_from_script_site_and_starting_scheme(sse, is_https)
            db_https_landing_url = ssla.landing_url
            is_https = False
            ssla = helper_script_site_lands.get_from_script_site_and_starting_scheme(sse, is_https)
            db_http_landing_url = ssla.landing_url
            print(f"--> from HTTPS starting scheme: landing url={db_https_landing_url}")
            print(f"--> from HTTP starting scheme: landing url={db_http_landing_url}")

            self.assertEqual(elaboration_https_landing_url, db_https_landing_url)
            self.assertEqual(elaboration_http_landing_url, db_http_landing_url)
        print("------- [4] END SCRIPT SITES INTEGRITY CHECK -------")


if __name__ == '__main__':
    unittest.main()
