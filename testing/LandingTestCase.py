import unittest
from entities.LandingResolver import LandingResolver


class LandingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.resolver = LandingResolver()
        self.website_list = [
            'login.microsoftonline.com',
            'auth.digidentity.eu',
            'clave-dninbrt.seg-social.gob.es',
            'youtube.it',
            'darklyrics.com'
        ]
        self.scriptsite_list = [
            'gmail.com'
        ]

    def test_domain_name_landing_page(self):
        for domain_name in self.website_list:
            print(f"Trying to resolve landing page of '{domain_name}':")
            results = self.resolver.resolve_landing_page(domain_name)

            # HTTPS
            print(f"**** via HTTPS *****")
            if results[0] is not None:
                (landing_url, redirection_path, hsts, ip) = results[0]
                print(f"HTTPS Landing url: {landing_url}")
                print(f"HTTPS IP: {ip.compressed}")
                print(f"Strict Transport Security: {hsts}")
                print(f"HTTPS Redirection path:")
                for index, url in enumerate(redirection_path):
                    print(f"----> [{index + 1}/{len(redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTPS...")

            # HTTP
            print(f"***** via HTTP *****")
            if results[1] is not None:
                (landing_url, redirection_path, hsts, ip) = results[1]
                print(f"HTTP Landing url: {landing_url}")
                print(f"HTTP IP: {ip.compressed}")
                print(f"Strict Transport Security: {hsts}")
                print(f"HTTP Redirection path:")
                for index, url in enumerate(redirection_path):
                    print(f"----> [{index + 1}/{len(redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTP...")
            print()


if __name__ == '__main__':
    unittest.main()
