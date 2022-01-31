import unittest
from peewee import DoesNotExist
from exceptions.NoAliasFoundError import NoAliasFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_domain_name, helper_alias


class DomainNameAndAliasQueryTestCase(unittest.TestCase):
    def test_01_query_aliases_from_domain_name(self):
        print(f"\n------- [1] QUERY ALIASES FROM DOMAIN NAME -------")
        # PARAMETER
        domain_name = 'www.youtube.com'
        # QUERY
        print(f"Parameter: {domain_name}")
        try:
            dnes = helper_alias.get_all_aliases_from_name(domain_name)
            for i, dne in enumerate(dnes):
                print(f"alias[{i + 1}/{len(dnes)}]: {dne.string}")
        except (DoesNotExist, NoAliasFoundError) as e:
            print(f"!!! {str(e)} !!!")
        print(f"------- [1] END QUERY ALIASES FROM DOMAIN NAME -------")

    def test_02_query_access_path_from_domain_name(self):
        print(f"\n------- [2] QUERY ACCESS PATH FROM DOMAIN NAME -------")
        # PARAMETER
        domain_name = 'www.youtube.com'
        # QUERY
        print(f"Parameter: {domain_name}")
        try:
            domain_name_entity = helper_domain_name.get(domain_name)
            try:
                iaes, dnes = helper_domain_name.resolve_access_path(domain_name_entity, get_only_first_address=False)
                print(f"Access path of domain name: {domain_name}")
                for i, dne in enumerate(dnes):
                    print(f"path[{i + 1}/{len(dnes)}]: {dne.string}")
                ip_addresses = set(map(lambda iae: iae.exploded_notation, iaes))
                print(f"IPs resolved: {str(ip_addresses)}")
            except NoAvailablePathError as e:
                print(f"!!! {str(e)} !!!")
        except DoesNotExist as exc:
            print(f"!!! {str(exc)} !!!")
        print(f"------- [2] END QUERY ACCESS PATH FROM DOMAIN NAME -------")


if __name__ == '__main__':
    unittest.main()
