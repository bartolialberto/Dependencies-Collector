import unittest
from utils import requests_utils


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.domain_name_list = ['login.microsoftonline.com', 'auth.digidentity.eu', 'clave-dninbrt.seg-social.gob.es']

    def test_landing_page(self):
        for domain_name in self.domain_name_list:
            print(f"Trying to connect to domain '{domain_name}' via https:")
            try:
                landing_url, redirection_path, hsts = requests_utils.resolve_landing_page(domain_name)
                print(f"Landing url: {landing_url}")
                print(f"HTTPS Strict Transport Security: {hsts}")
                print(f"Redirection path:")
                for index, url in enumerate(redirection_path):
                    print(f"[{index + 1}/{len(redirection_path)}]: {url}")
            except Exception as exc:
                print(f"!!! {str(exc)} !!!")
            print()


if __name__ == '__main__':
    unittest.main()
