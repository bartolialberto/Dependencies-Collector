import unittest
from entities.DomainName import DomainName
from entities.enums.TypesRR import TypesRR
from entities.resolvers.DnsResolver import DnsResolver
from persistence import helper_paths, helper_domain_name


class APathIntegrityTestCase(unittest.TestCase):
    """
    DEFINITIVE TEST

    """
    domain_name = None
    dns_resolver = None
    path = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.domain_name = DomainName('platform.twitter.com.')
        # ELABORATION
        cls.dns_resolver = DnsResolver(True)
        cls.path = cls.dns_resolver.do_query(cls.domain_name.string, TypesRR.A)
        print(f"{cls.path.stamp()}")
        cls.dns_resolver.cache.add_path(cls.path)
        helper_paths.insert_a_path(cls.path)

    def test_01_from_cache(self):
        print("\n------- [1] START RETRIEVING FROM CACHE TEST -------")
        result_path = self.dns_resolver.cache.resolve_path(self.domain_name, TypesRR.A)
        print(f"{result_path.stamp()}")
        self.assertEqual(self.path, result_path)
        print("------- [1] END RETRIEVING FROM CACHE TEST -------")

    def test_02_from_database(self):
        print("\n------- [2] START RETRIEVING FROM DATABASE TEST -------")
        result_path = helper_domain_name.resolve_a_path(self.domain_name)
        print(f"{result_path.stamp()}")
        self.assertEqual(self.path, result_path)
        print("------- [2] END RETRIEVING FROM DATABASE TEST -------")


if __name__ == '__main__':
    unittest.main()
