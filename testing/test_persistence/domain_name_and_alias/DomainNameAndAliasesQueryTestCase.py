import unittest
from peewee import DoesNotExist
from exceptions.NoAliasFoundError import NoAliasFoundError
from persistence import helper_domain_name, helper_alias


class DomainNameAndAliasesQueryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_name = 'dns.unipd.it'

    def test_1_get_first_alias(self):
        print(f"\nSTART GETTING FIRST ALIAS CHECK TEST with parameter = {self.domain_name}")
        try:
            alias = helper_alias.get_alias_from_name(self.domain_name)
            print(f"alias = {alias.name}")
        except (DoesNotExist, NoAliasFoundError) as e:
            print(f"!!! {str(e)} !!!")
        print(f"END GETTING FIRST ALIAS CHECK TEST")

    def test_2_get_aliases(self):
        print(f"\nSTART GETTING ALL ALIASES CHECK TEST with parameter = {self.domain_name}")
        try:
            aliases = helper_alias.get_all_aliases_from_name(self.domain_name)
            for i, alias in enumerate(aliases):
                print(f"[{i+1}/{len(aliases)}] = {alias.name}")
        except (DoesNotExist, NoAliasFoundError) as e:
            print(f"!!! {str(e)} !!!")
        print(f"END GETTING ALL ALIASES CHECK TEST")

    def test_3_resolving_access_path(self):
        print(f"\nSTART RESOLVING ACCESS PATH TEST with parameter = {self.domain_name}")
        try:
            dne = helper_domain_name.get(self.domain_name)
            try:
                iae, dne_chain = helper_domain_name.resolve_access_path(dne)
                print(f"Resolved path lead to: {iae.exploded_notation}")
                print(f"Resolved path:")
                for i, dne in enumerate(dne_chain):
                    print(f"[{i+1}]: {dne.name}")
            except DoesNotExist as e:
                print(f"!!! {str(e)} !!!")
        except DoesNotExist as exc:
            print(f"!!! {str(exc)} !!!")
        print(f"END RESOLVING ACCESS PATH TEST")


if __name__ == '__main__':
    unittest.main()
