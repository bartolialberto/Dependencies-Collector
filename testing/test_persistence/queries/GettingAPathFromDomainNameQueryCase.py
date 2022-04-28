import unittest
from entities.DomainName import DomainName
from persistence import helper_domain_name, helper_ip_address


class GettingAPathFromDomainNameQueryCase(unittest.TestCase):
    dne = None
    domain_name = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.domain_name = DomainName('www.netflix.com.')
        # ELABORATION
        cls.dne = helper_domain_name.get(cls.domain_name)
        cls.a_path = helper_domain_name.resolve_a_path(cls.dne, as_persistence_entities=False)
        cls.cname_dnes, cls.iaes = helper_domain_name.resolve_a_path(cls.dne, as_persistence_entities=True)

    def test_01_integrity_between_as_persistence_entities_flag(self):
        print(f"\n------- START QUERY 1 -------")
        cnames_from_a_path = list(map(lambda dn: dn.string, self.a_path.get_cname_chain(as_resource_records=False)))
        addresses_from_a_path = set(map(lambda ia: ia.exploded, self.a_path.get_resolution().values))
        print(f"from APath: {self.a_path.stamp()}")

        cnames_from_persistence = list(map(lambda dne: dne.string, self.cname_dnes))
        addresses_from_persistence = set(map(lambda iae: iae.exploded_notation, self.iaes))
        print(f"from   DB:  ", end='')
        if len(cnames_from_persistence) == 0:
            print(f"{cnames_from_persistence[0]}")
        else:
            for i, s in enumerate(cnames_from_persistence):
                if i == len(cnames_from_persistence)-1:
                    print(f"{s}", end='')
                else:
                    print(f"{s} --CNAME-> ", end='')
        print(f" ==A=> {str(addresses_from_persistence)}")

        self.assertListEqual(cnames_from_a_path, cnames_from_persistence)
        self.assertSetEqual(addresses_from_a_path, addresses_from_persistence)
        print(f"------- END QUERY 1 -------")

    def test_02_integrity_between_as_persistence_entities_flag_of_reversed(self):
        print(f"\n------- START QUERY 2 -------")
        for ip_address in self.a_path.get_resolution().values:
            print(f"For {ip_address.exploded}")
            iae = helper_ip_address.get(ip_address)
            tmp = helper_ip_address.resolve_reversed_a_path(iae, as_reversed=False)
            from_elaboration = list(map(lambda dn: dn.string, tmp))
            true_elaboration = list(map(lambda dn: dn.string, self.a_path.get_cname_chain(as_resource_records=False)))
            print(f"--> true values: {true_elaboration}")
            print(f"--> elaboration: {from_elaboration}")
            self.assertListEqual(true_elaboration, from_elaboration)
        print(f"------- END QUERY 2 -------")


if __name__ == '__main__':
    unittest.main()
