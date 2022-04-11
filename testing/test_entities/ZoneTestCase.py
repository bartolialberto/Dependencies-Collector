import unittest
from entities.DomainName import DomainName
from entities.enums.TypesRR import TypesRR
from entities.resolvers.DnsResolver import DnsResolver
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.NotWantedTLDError import NotWantedTLDError
from exceptions.UnknownReasonError import UnknownReasonError


class ZoneTestCase(unittest.TestCase):
    name_for_comparison = None
    dns_resolver = None
    name = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.name = 'unipd.it'
        cls.name_for_comparison = 'UNIPD.IT'
        # DNS QUERY FOR DATA
        cls.dns_resolver = DnsResolver(True)
        try:
            cls.path = cls.dns_resolver.do_query(cls.name, TypesRR.NS)
        except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
            cls.fail(e)
        try:
            cls.path_for_comparison = cls.dns_resolver.do_query(cls.name_for_comparison, TypesRR.NS)
        except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
            cls.fail(e)
        # compute Zone objects
        try:
            cls.zone, to_be_added, error_logs = cls.dns_resolver.resolve_zone(DomainName(cls.name))
        except (NotWantedTLDError, NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
            cls.fail(e)
        try:
            cls.zone_for_comparison, to_be_added_for_comparison, error_logs_for_comparison = cls.dns_resolver.resolve_zone(DomainName(cls.name_for_comparison))
        except (NotWantedTLDError, NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
            cls.fail(e)
        print(f"MAIN PARAMETER: {cls.name}")
        print(f"PARAMETER FOR COMPARISON: {cls.name_for_comparison}\n")

    def test_01_equality_of_path(self):
        print(f"\n------- [1] START PATH EQUALITY TEST -------")
        print(f"path of parameter: {self.path.stamp()}")
        print(f"path of comparison: {self.path_for_comparison.stamp()}")
        self.assertEqual(self.path, self.path_for_comparison)
        print(f"------- [1] END PATH EQUALITY TEST -------")

    def test_02_hash_equality_of_path(self):
        print(f"\n------- [2] START PATH HASH TEST -------")
        print(f"path of parameter: {self.path.stamp()}")
        print(f"path of comparison: {self.path_for_comparison.stamp()}")
        print(f"hash of parameter: {self.path.__hash__()}")
        print(f"hash of comparison: {self.path_for_comparison.__hash__()}")
        self.assertEqual(self.path.__hash__(), self.path_for_comparison.__hash__())
        # test integrity between __eq__ and __hash__
        self.assertEqual(self.path.__hash__() == self.path_for_comparison.__hash__(), self.path == self.path_for_comparison)
        print(f"------- [2] END PATH HASH TEST -------")

    def test_03_equality_of_zone(self):
        print(f"\n------- [3] START ZONE EQUALITY TEST -------")
        print(f"zone parameter: {self.zone.name_path.stamp()}")
        for i, a_path in enumerate(self.zone.name_servers):
            print(f"A path[{i+1}/{len(self.zone.name_servers)}]: {a_path.stamp()}")
        print(f"\nzone comparison: {self.zone_for_comparison.name_path.stamp()}")
        for i, a_path in enumerate(self.zone_for_comparison.name_servers):
            print(f"A path[{i+1}/{len(self.zone_for_comparison.name_servers)}]: {a_path.stamp()}")
        self.assertEqual(self.zone, self.zone_for_comparison)
        print(f"------- [3] END ZONE EQUALITY TEST -------")

    def test_04_hash_equality_of_zone(self):
        print(f"\n------- [4] START ZONE HASH TEST -------")
        print(f"zone parameter hash: {self.zone.__hash__()}")
        print(f"zone comparison hash: {self.zone_for_comparison.__hash__()}")
        self.assertEqual(self.zone.__hash__(), self.zone_for_comparison.__hash__())
        # test integrity between __eq__ and __hash__
        self.assertEqual(self.zone.__hash__() == self.zone_for_comparison.__hash__(), self.zone == self.zone_for_comparison)
        print(f"------- [4] END ZONE HASH TEST -------")

    def test_05_parse_every_domain_name(self):
        print(f"\n------- [5] START PARSING EVERY DOMAIN NAME TEST -------")
        # PARAMETERS
        root_included = True
        zone_included = True
        tlds = True
        # TEST
        domain_names = self.zone.parse_every_domain_name(with_zone_name=zone_included, root_included=root_included, tld_included=tlds)
        for i, domain_name in enumerate(domain_names):
            print(f"domain name[{i+1}/{len(domain_names)}]: {domain_name}")
        print(f"------- [5] START PARSING EVERY DOMAIN NAME TEST -------")


if __name__ == '__main__':
    unittest.main()
