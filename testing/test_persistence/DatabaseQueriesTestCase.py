import unittest
from peewee import DoesNotExist
from persistence import helper_zone, helper_domain_name, helper_alias


class DatabaseQueriesTestCase(unittest.TestCase):
    def test_01_query_zone_dependencies_from_domain_name(self):
        print(f"\n------- [1] QUERY ZONE DEPENDENCIES FROM DOMAIN NAME -------")
        # PARAMETER
        domain_name = 'mail.google.it'
        # QUERY
        try:
            zes = helper_zone.get_zone_dependencies_of(domain_name)
            print(f"Zone dependencies of domain name: {domain_name}")
            for i, ze in enumerate(zes):
                print(f"zone[{i + 1}/{len(zes)}]: {ze.name}")
        except DoesNotExist as e:
            print(f"!!! {str(e)} !!!")
        print(f"------- [1] END QUERY ZONE DEPENDENCIES FROM DOMAIN NAME -------")

    def test_02_query_aliases_from_domain_name(self):
        print(f"\n------- [2] QUERY ALIAS AND ACCESS PATH FROM DOMAIN NAME -------")
        # PARAMETER
        domain_name = 'mail.google.it'
        # QUERY
        try:
            dnes = helper_alias.get_all_aliases_from_name(domain_name)
            print(f"All aliases of domain name: {domain_name}")
            for i, dne in enumerate(dnes):
                print(f"alias[{i + 1}/{len(dne)}]: {dne.name}")
        except DoesNotExist as e:
            print(f"!!! {str(e)} !!!")
        print(f"------- [2] END QUERY ALIAS AND ACCESS PATH FROM DOMAIN NAME -------")

    def test_03_query_access_path_from_domain_name(self):
        print(f"\n------- [3] QUERY ACCESS PATH FROM DOMAIN NAME -------")
        # PARAMETER
        domain_name = 'dns.nic.it'
        # QUERY
        try:
            domain_name_entity = helper_domain_name.get(domain_name)
            try:
                iae, dnes = helper_domain_name.resolve_access_path(domain_name_entity)
                print(f"Access path of domain name: {domain_name}")
                for i, dne in enumerate(dnes):
                    print(f"path[{i + 1}/{len(dnes)}]: {dne.name}")
                print(f"IP resolved: {iae.exploded_notation}")
            except DoesNotExist as e:
                print(f"!!! {str(e)} !!!")
        except DoesNotExist as exc:
            print(f"!!! {str(exc)} !!!")
        print(f"------- [3] END QUERY ACCESS PATH FROM DOMAIN NAME -------")


if __name__ == '__main__':
    unittest.main()
