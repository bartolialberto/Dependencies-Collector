import unittest
from entities.DomainName import DomainName
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from entities.paths.builders.NSPathBuilder import NSPathBuilder
from entities.resolvers.DnsResolver import DnsResolver


class PathBuilderTestCase(unittest.TestCase):
    def test_something(self):
        dns_resolver = DnsResolver(False)
        param_dn = DomainName('cdn-auth.digidentity.eu.')
        param_dn = DomainName('pec.trentinolunch.it.')
        result = dns_resolver.resolve_domain_dependencies(param_dn)
        print(f"")


if __name__ == '__main__':
    unittest.main()
