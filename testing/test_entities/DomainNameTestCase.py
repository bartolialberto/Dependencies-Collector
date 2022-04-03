import unittest
from entities.DomainName import DomainName


class DomainNameTestCase(unittest.TestCase):
    for_comparison = None
    domain_name = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.domain_name = DomainName('.')
        cls.for_comparison = DomainName('units.it')
        print(f"PARAMETER: {cls.domain_name}")
        print(f"PARAMETER FOR COMPARISON: {cls.for_comparison}")

    def test_01_equality(self):
        print(f"\n------- [1] START EQUALITY TEST -------")
        print(f"standardized string of {self.domain_name.input_string}: {self.domain_name}")
        print(f"standardized string of {self.for_comparison.input_string}: {self.for_comparison}")
        self.assertEqual(self.domain_name, self.for_comparison)
        print(f"------- [1] END EQUALITY TEST -------")

    def test_02_hash_equality(self):
        print(f"\n------- [2] START EQUALITY TEST -------")
        print(f"hash of {self.domain_name}: {self.domain_name.__hash__()}")
        print(f"hash of {self.for_comparison}: {self.for_comparison.__hash__()}")
        self.assertEqual(self.domain_name.__hash__(), self.for_comparison.__hash__())
        # test integrity between __eq__ and __hash__
        self.assertEqual(self.domain_name.__hash__() == self.for_comparison.__hash__(), self.domain_name == self.for_comparison)
        print(f"------- [2] END EQUALITY TEST -------")

    def test_03_parse_subdomains_conf1(self):
        print(f"\n------- [3] START SUBDOMAINS PARSING TEST -------")
        # PARAMETERS
        root_included = True
        self_included = True
        # TESTING
        print(f"PARAMETERS ---")
        print(f"root_included: {root_included}")
        print(f"self_included: {self_included}")
        print(f"SUBDOMAINS PARSED:")
        subdomains = self.domain_name.parse_subdomains(root_included=root_included, self_included=self_included)
        for i, dn in enumerate(subdomains):
            print(f"[{i+1}/{len(subdomains)}]: {dn.string}")
        print(f"------- [3] END SUBDOMAINS PARSING TEST -------")

    def test_04_parse_subdomains_conf2(self):
        print(f"\n------- [4] START SUBDOMAINS PARSING TEST -------")
        # PARAMETERS
        root_included = True
        self_included = False
        # TESTING
        print(f"PARAMETERS ---")
        print(f"root_included: {root_included}")
        print(f"self_included: {self_included}")
        print(f"SUBDOMAINS PARSED:")
        subdomains = self.domain_name.parse_subdomains(root_included=root_included, self_included=self_included)
        for i, dn in enumerate(subdomains):
            print(f"[{i+1}/{len(subdomains)}]: {dn.string}")
        print(f"------- [4] END SUBDOMAINS PARSING TEST -------")

    def test_05_parse_subdomains_conf3(self):
        print(f"\n------- [5] START SUBDOMAINS PARSING TEST -------")
        # PARAMETERS
        root_included = False
        self_included = False
        # TESTING
        print(f"PARAMETERS ---")
        print(f"root_included: {root_included}")
        print(f"self_included: {self_included}")
        print(f"SUBDOMAINS PARSED:")
        subdomains = self.domain_name.parse_subdomains(root_included=root_included, self_included=self_included)
        for i, dn in enumerate(subdomains):
            print(f"[{i+1}/{len(subdomains)}]: {dn.string}")
        print(f"------- [5] END SUBDOMAINS PARSING TEST -------")

    def test_06_parse_subdomains_conf4(self):
        print(f"\n------- [6] START SUBDOMAINS PARSING TEST -------")
        # PARAMETERS
        root_included = False
        self_included = True
        # TESTING
        print(f"PARAMETERS ---")
        print(f"root_included: {root_included}")
        print(f"self_included: {self_included}")
        print(f"SUBDOMAINS PARSED:")
        subdomains = self.domain_name.parse_subdomains(root_included=root_included, self_included=self_included)
        for i, dn in enumerate(subdomains):
            print(f"[{i+1}/{len(subdomains)}]: {dn.string}")
        print(f"------- [3] END SUBDOMAINS PARSING TEST -------")

    def test_07_is_tld(self):
        print(f"\n------- [7] START IS TLD TEST -------")
        print(f"Parameter: {self.domain_name}")
        result = self.domain_name.is_tld()
        print(f"Is TLD? {result}")
        print(f"------- [7] END IS TLD TEST -------")

    def test_08_http_request(self):
        print(f"\n------- [8] START HTTP REQUEST TEST -------")
        # PARAMETERS
        https = True
        # TESTING
        print(f"Parameter: {self.domain_name}, HTTPS: {https}")
        result = self.domain_name.construct_http_url(as_https=https)
        print(f"Result: {result}")
        print(f"------- [8] END HTTP REQUEST TEST -------")


if __name__ == '__main__':
    unittest.main()
