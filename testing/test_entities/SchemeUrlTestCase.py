import unittest
from entities.SchemeUrl import SchemeUrl


class SchemeUrlTestCase(unittest.TestCase):
    for_comparison = None
    url = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        str_parameter = 'https://mail.google.com/mail/u/0/#inbox'
        str_for_comparison = 'http://mail.google.com/mail/u/0/#inbox/'
        # ELABORATION
        cls.url = SchemeUrl(str_parameter)
        cls.for_comparison = SchemeUrl(str_for_comparison)
        print(f"PARAMETER: {str_parameter}")
        print(f"PARAMETER FOR COMPARISON: {str_for_comparison}")

    def test_01_equality(self):
        print(f"\n------- START TEST 1 -------")
        print(f"parameter: {self.url}")
        print(f"comparison: {self.for_comparison}")
        self.assertEqual(self.url, self.for_comparison)
        print(f"------- END TEST 1 -------")

    def test_02_hash_equality(self):
        print(f"\n------- START TEST 2 -------")
        print(f"hash of parameter: {self.url.__hash__()}")
        print(f"hash of comparison: {self.for_comparison.__hash__()}")
        self.assertEqual(self.url.__hash__(), self.for_comparison.__hash__())
        print(f"------- END TEST 2 -------")

    def test_03_hash_and_eq_consistency(self):
        print(f"\n------- START TEST 3 -------")
        self.assertEqual(self.url.__hash__() == self.for_comparison.__hash__(), self.url == self.for_comparison)
        print(f"------- END TEST 3 -------")

    def test_04_stamp_landing_scheme(self):
        print(f"\n------- START TEST 4 -------")
        print(f"Stamp scheme of parameter: {self.url.stamp_landing_scheme()}")
        print(f"Stamp scheme of comparison: {self.url.stamp_landing_scheme()}")
        self.assertEqual(self.url.stamp_landing_scheme(), self.url.stamp_landing_scheme())
        print(f"------- END TEST 4 -------")

    def test_05_domain_name(self):
        print(f"\n------- START TEST 5 -------")
        print(f"Domain name of parameter: {self.url.domain_name()}")
        print(f"Domain name of comparison: {self.for_comparison.domain_name()}")
        self.assertEqual(self.url.domain_name(), self.for_comparison.domain_name())
        print(f"------- END TEST 5 -------")


if __name__ == '__main__':
    unittest.main()
