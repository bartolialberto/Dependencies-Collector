import unittest
from utils import domain_name_utils


class MyTestCase(unittest.TestCase):
    def test_correctness(self):
        domain_name = 'tracking-protection.cdn.mozilla.net.'
        # domain_name = 'firefox.settings.services.mozilla.com'     # No
        is_right = domain_name_utils.is_grammatically_correct(domain_name)
        print(f"Domain name: {domain_name}")
        print(f"Is that right? {is_right}")

    def test_deductiong_from_url(self):
        url = 'https://tracking-protection.cdn.mozilla.net/ads-track-digest256/1633028676'
        result = domain_name_utils.deduct_domain_name(url)
        is_right = domain_name_utils.is_grammatically_correct(result)
        print(f"url: {url}")
        print(f"deducted domain name: {result}")
        print(f"Is that right? {is_right}")


if __name__ == '__main__':
    unittest.main()
