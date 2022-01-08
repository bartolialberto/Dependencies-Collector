import unittest
from peewee import DoesNotExist
from persistence import helper_domain_name, helper_alias


class DomainNameAndAliasesQueryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_name = 'dns.unipd.it'

    def test_1_get_first_alias(self):
        print(f"\nSTART GETTING FIRST ALIAS CHECK TEST with parameter = {self.domain_name}")
        try:
            dne = helper_domain_name.get(self.domain_name)
            try:
                alias = helper_alias.get_alias_from_name(dne)
                print(f"alias = {alias.name}")
            except DoesNotExist:
                print(f"!!! No alias for {self.domain_name} !!!")
        except DoesNotExist:
            print(f"!!! domain name '{self.domain_name}'  is not present in the database !!!")
        print(f"END GETTING FIRST ALIAS CHECK TEST")

    def test_2_get_aliases(self):
        print(f"\nSTART GETTING ALL ALIASES CHECK TEST with parameter = {self.domain_name}")
        try:
            dne = helper_domain_name.get(self.domain_name)
            try:
                aliases = helper_alias.get_all_aliases_from_name(dne)
                for i, alias in enumerate(aliases):
                    print(f"[{i+1}/{len(aliases)}] = {alias.name}")
            except DoesNotExist:
                print(f"No alias for {self.domain_name}")
        except DoesNotExist:
            print(f"domain name '{self.domain_name}'  is not present in the database")
        print(f"END GETTING ALL ALIASES CHECK TEST")

    def test_3_resolving_access_path(self):
        print(f"\nSTART RESOLVING ACCESS PATH TEST with parameter = {self.domain_name}")
        try:
            dne = helper_domain_name.get(self.domain_name)
            try:
                iae = helper_domain_name.resolve_access_path(dne)
                print(f"Resolved path lead to: {iae.exploded_notation}")
            except DoesNotExist:
                print(f"No path resolved")
        except DoesNotExist:
            print(f"domain name '{self.domain_name}'  is not present in the database")
        print(f"END RESOLVING ACCESS PATH TEST")


if __name__ == '__main__':
    unittest.main()
