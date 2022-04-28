import unittest
from peewee import DoesNotExist
from entities.DomainName import DomainName
from persistence import helper_domain_name, helper_access


class AccessAssociationErrorCase(unittest.TestCase):
    def test_01_set_access_association_to_null(self):
        print(f"\n------- START TEST 1 -------")
        # PARAMETERS
        for_domain_name = DomainName('mx.cert.legalmail.it.')
        # ELABORATION
        print(f"Domain name: {for_domain_name}")
        try:
            dne = helper_domain_name.get(for_domain_name)
            aas = helper_access.get_of_entity_domain_name(dne)
            if len(aas) == 0:
                helper_access.insert(dne, None)
            else:
                for i, aa in enumerate(aas):
                    if i == 0:
                        aa.ip_address = None
                        aa.save()
                    else:
                        aa.delete_instance()
        except DoesNotExist:
            dne = helper_domain_name.insert(for_domain_name)
            helper_access.insert(dne, None)
        print(f"------- END TEST 1 -------")


if __name__ == '__main__':
    unittest.main()
