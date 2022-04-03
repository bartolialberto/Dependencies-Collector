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
        print(f"\n------- [1] START EQUALITY TEST -------")
        print(f"parameter: {self.url}")
        print(f"comparison: {self.for_comparison}")
        self.assertEqual(self.url, self.for_comparison)
        print(f"------- [1] END EQUALITY TEST -------")

    def test_02_hash_equality(self):
        print(f"\n------- [2] START HASH TEST -------")
        print(f"hash of parameter: {self.url.__hash__()}")
        print(f"hash of comparison: {self.for_comparison.__hash__()}")
        self.assertEqual(self.url.__hash__(), self.for_comparison.__hash__())
        print(f"------- [2] END HASH TEST -------")

    def test_03_hash_and_eq_consistency(self):
        print(f"\n------- [3] START HASH-EQ CONSISTENCY TEST -------")
        self.assertEqual(self.url.__hash__() == self.for_comparison.__hash__(), self.url == self.for_comparison)
        print(f"------- [3] END HASH-EQ CONSISTENCY TEST -------")

    def test_05_stamp_landing_scheme(self):
        print(f"\n------- [5] START STAMPING LANDING SCHEME TEST -------")
        print(f"Stamp scheme of parameter: {self.url.stamp_landing_scheme()}")
        print(f"Stamp scheme of comparison: {self.url.stamp_landing_scheme()}")
        self.assertEqual(self.url.stamp_landing_scheme(), self.url.stamp_landing_scheme())
        print(f"------- [5] END STAMPING LANDING SCHEME TEST -------")

    def test_06_domain_name(self):
        print(f"\n------- [6] START DOMAIN NAME TEST -------")
        print(f"Domain name of parameter: {self.url.domain_name()}")
        print(f"Domain name of comparison: {self.for_comparison.domain_name()}")
        self.assertEqual(self.url.domain_name(), self.for_comparison.domain_name())
        print(f"------- [6] END DOMAIN NAME TEST -------")


if __name__ == '__main__':
    unittest.main()
