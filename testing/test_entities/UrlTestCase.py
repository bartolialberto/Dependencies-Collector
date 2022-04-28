import unittest
from entities.Url import Url


class UrlTestCase(unittest.TestCase):
    for_comparison = None
    url = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        str_parameter = 'https://mail.google.com/mail/u/0/#inbox'
        str_for_comparison = 'mail.google.com/mail/u/0/#inbox/'
        # ELABORATION
        cls.url = Url(str_parameter)
        cls.for_comparison = Url(str_for_comparison)
        print(f"PARAMETER: {str_parameter}")
        print(f"PARAMETER FOR COMPARISON: {str_for_comparison}")

    def test_01_equality(self):
        print(f"\n------- START TEST 1 -------")
        print(f"second component of parameter: {self.url}")
        print(f"second component of comparison: {self.for_comparison}")
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

    def test_04_second_component(self):
        print(f"\n------- START TEST 4 -------")
        print(f"second component of parameter: {self.url.second_component()}")
        print(f"second component of comparison: {self.for_comparison.second_component()}")
        self.assertEqual(self.url.second_component(), self.for_comparison.second_component())
        print(f"------- END TEST 4 -------")

    def test_05_https(self):
        print(f"\n------- START TEST 5 -------")
        print(f"HTTPS url of parameter: {self.url.https()}")
        print(f"HTTPS url of comparison: {self.for_comparison.https()}")
        self.assertEqual(self.url.https(), self.for_comparison.https())
        print(f"------- END TEST 5 -------")

    def test_06_http(self):
        print(f"\n------- START TEST 6 -------")
        print(f"HTTP url of parameter: {self.url.http()}")
        print(f"HTTP url of comparison: {self.for_comparison.http()}")
        self.assertEqual(self.url.http(), self.for_comparison.http())
        print(f"------- END TEST 6 -------")

    def test_07_domain_name(self):
        print(f"\n------- START TEST 7 -------")
        print(f"Domain name of parameter: {self.url.domain_name()}")
        print(f"Domain name of comparison: {self.for_comparison.domain_name()}")
        self.assertEqual(self.url.domain_name(), self.for_comparison.domain_name())
        print(f"------- END TEST 7 -------")


if __name__ == '__main__':
    unittest.main()
