import unittest
from utils import domain_name_utils


class DomainNameTestCase(unittest.TestCase):
    # EXAMPLES
    # 'tracking-protection.cdn.mozilla.net.'
    # 'firefox.settings.services.mozilla.com'     # No
    # 'c.ns.c10r.facebook.com.'     # No
    def test_1_correctness(self):
        print(f"\n------- [1] START DOMAIN NAME CORRECTNESS TEST -------")
        # PARAMETERS
        domain_name = 'c.ns.c10r.facebook.com.'     # No
        # ELABORATION
        is_right = domain_name_utils.is_grammatically_correct(domain_name)
        print(f"Domain name: {domain_name}")
        print(f"Is that right? {is_right}")
        self.assertTrue(is_right)
        print(f"------- [1] END DOMAIN NAME CORRECTNESS TEST -------")

    # EXAMPLES
    # 'https://tracking-protection.cdn.mozilla.net/ads-track-digest256/1633028676'
    # 'https://idp-cineca.units.it/idp/profile/SAML2/Redirect/SSO?execution=e1s2'
    # 'idp-cineca.units.it/idp/profile/SAML2/Redirect/SSO?execution=e1s2'
    def test_2_deducting_from_url(self):
        print(f"\n------- [2] START DEDUCTING URL TEST -------")
        # PARAMETERS
        url = 'https://idp-cineca.units.it/idp/profile/SAML2/Redirect/SSO?execution=e1s2'
        url = 'https://www.youtube.it/feed/explore/'
        # ELABORATION
        result = domain_name_utils.deduct_domain_name(url)
        is_right = domain_name_utils.is_grammatically_correct(result)
        print(f"url: {url}")
        print(f"deducted domain name: {result}")
        print(f"Is that right? {is_right}")
        self.assertTrue(is_right)
        print(f"------- [2] END DEDUCTING URL TEST -------")

    def test_3_insert_trailing_point(self):
        print(f"\n------- [3] START INSERTING TRAILING POINT TEST -------")
        # PARAMETERS
        domain_name = '.'
        # ELABORATION
        result = domain_name_utils.insert_trailing_point(domain_name)
        print(f"Domain name: {domain_name}")
        print(f"Result: {result}")
        print(f"------- [3] END INSERTING TRAILING POINT TEST -------")

    def test_4_eliminate_trailing_point(self):
        print(f"\n------- [4] START ELIMINATING TRAILING POINT TEST -------")
        # PARAMETERS
        domain_name = 'it..'
        # ELABORATION
        result = domain_name_utils.eliminate_trailing_point(domain_name)
        print(f"Domain name: {domain_name}")
        print(f"Result: {result}")
        print(f"------- [4] END ELIMINATING TRAILING POINT TEST -------")

    def test_4_is_tld(self):
        print(f"\n------- [3] START QUERYING IF IT IS TLD TEST -------")
        # PARAMETERS
        domain_name = 'units.it.'
        # ELABORATION
        result = domain_name_utils.is_tld(domain_name)
        print(f"Domain name: {domain_name}")
        print(f"Result: {result}")
        print(f"------- [3] END QUERYING IF IT IS TLD TEST -------")


if __name__ == '__main__':
    unittest.main()
