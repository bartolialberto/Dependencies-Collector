import unittest
from entities.resolvers.DnsResolver import DnsResolver
from entities.resolvers.LandingResolver import LandingResolver


class LandingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        dns_resolver = DnsResolver(True)
        self.resolver = LandingResolver(dns_resolver)
        self.web_site_list = [
            'google.it/doodles',
            'www.youtube.it/feed/explore'
        ]
        self.script_site_list = [
            'www.youtube.com/s/desktop/5650b92e/jsbin/spf.vflset/spf.js',
            'www.youtube.com/s/player/f93a7034/player_ias.vflset/it_IT/base.js',
            'ssl.google-analytics.com/ga.js'
        ]

    def test_1_web_sites_landing(self):
        print(f"\n------- [1] START WEB SITE LANDING TEST -------")
        for i, web_site in enumerate(self.web_site_list):
            print(f"Trying to resolve landing of websites[{i+1}/{len(self.web_site_list)}]: {web_site}")
            results = self.resolver.resolve_site(web_site)

            # HTTPS
            print(f"**** via HTTPS *****")
            https_result = results.https
            if https_result is not None:
                print(f"HTTPS Landing url: {https_result.url}")
                print(f"HTTPS Access Path: {https_result.stamp_access_path()}")
                print(f"Strict Transport Security: {https_result.hsts}")
                print(f"HTTPS Redirection path:")
                for index, url in enumerate(https_result.redirection_path):
                    print(f"----> [{index + 1}/{len(https_result.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTPS...")

            # HTTP
            print(f"***** via HTTP *****")
            http_result = results.http
            if http_result is not None:
                print(f"HTTP Landing url: {http_result.url}")
                print(f"HTTP Access Path: {http_result.stamp_access_path()}")
                print(f"Strict Transport Security: {http_result.hsts}")
                print(f"HTTP Redirection path:")
                for index, url in enumerate(http_result.redirection_path):
                    print(f"----> [{index + 1}/{len(http_result.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTP...")
            if i != len(self.web_site_list)-1:
                print()
        print(f"------- [1] END WEB SITE LANDING TEST -------")

    def test_2_script_sites_landing(self):
        print(f"\n------- [2] START SCRIPT SITE LANDING TEST -------")
        for i, script_site in enumerate(self.script_site_list):
            print(f"Trying to resolve landing of script site[{i+1}/{len(self.script_site_list)}]: {script_site}:")
            results = self.resolver.resolve_site(script_site)

            # HTTPS
            print(f"**** via HTTPS *****")
            https_result = results.https
            if https_result is not None:
                print(f"HTTPS Landing url: {https_result.url}")
                print(f"HTTPS Access Path: {https_result.stamp_access_path()}")
                print(f"Strict Transport Security: {https_result.hsts}")
                print(f"HTTPS Redirection path:")
                for index, url in enumerate(https_result.redirection_path):
                    print(f"----> [{index + 1}/{len(https_result.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTPS...")

            # HTTP
            print(f"***** via HTTP *****")
            http_result = results.http
            if http_result is not None:
                print(f"HTTP Landing url: {http_result.url}")
                print(f"HTTP Access Path: {http_result.stamp_access_path()}")
                print(f"Strict Transport Security: {http_result.hsts}")
                print(f"HTTP Redirection path:")
                for index, url in enumerate(http_result.redirection_path):
                    print(f"----> [{index + 1}/{len(http_result.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTP...")
            if i != len(self.script_site_list)-1:
                print()
        print(f"------- [2] END SCRIPT SITE LANDING TEST -------")


if __name__ == '__main__':
    unittest.main()
