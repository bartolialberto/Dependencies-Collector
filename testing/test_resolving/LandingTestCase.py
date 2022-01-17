import unittest
from entities.resolvers.LandingResolver import LandingResolver


class LandingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.resolver = LandingResolver()
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
            results = self.resolver.resolve_web_site(web_site)

            # HTTPS
            print(f"**** via HTTPS *****")
            https_result = results[0]
            if https_result is not None:
                print(f"HTTPS Landing url: {https_result.name}")
                print(f"HTTPS WebServer: {https_result.server}")
                print(f"HTTPS IP: {https_result.ip}")
                print(f"Strict Transport Security: {https_result.hsts}")
                print(f"HTTPS Redirection path:")
                for index, url in enumerate(https_result.redirection_path):
                    print(f"----> [{index + 1}/{len(https_result.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTPS...")

            # HTTP
            print(f"***** via HTTP *****")
            http_result = results[1]
            if http_result is not None:
                print(f"HTTP Landing url: {http_result.name}")
                print(f"HTTP WebServer: {http_result.server}")
                print(f"HTTP IP: {http_result.ip}")
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
            results = self.resolver.resolve_web_site(script_site)

            # HTTPS
            print(f"**** via HTTPS *****")
            https_result = results[0]
            if https_result is not None:
                print(f"HTTPS Landing url: {https_result.name}")
                print(f"HTTPS ScriptServer: {https_result.server}")
                print(f"HTTPS IP: {https_result.ip}")
                print(f"Strict Transport Security: {https_result.hsts}")
                print(f"HTTPS Redirection path:")
                for index, url in enumerate(https_result.redirection_path):
                    print(f"----> [{index + 1}/{len(https_result.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTPS...")

            # HTTP
            print(f"***** via HTTP *****")
            http_result = results[1]
            if http_result is not None:
                print(f"HTTP Landing url: {http_result.name}")
                print(f"HTTP ScriptServer: {http_result.server}")
                print(f"HTTP IP: {http_result.ip}")
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
