import unittest
from peewee import DoesNotExist
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_domain_name, helper_ip_address


class DomainNameAndAliasQueryTestCase(unittest.TestCase):
    def test_1_query_access_path_from_domain_name(self):
        print(f"\n------- [1] QUERY ACCESS PATH FROM DOMAIN NAME -------")
        # PARAMETER
        domain_name = 'platform.twitter.com.'
        domain_name = 'ossigeno.acantho.sys.'
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
        print(f"------- [1] END QUERY ACCESS PATH FROM DOMAIN NAME -------")

    def test_2_query_reversed_access_path_from_ip_address(self):
        print(f"\n------- [1] QUERY REVERSED ACCESS PATH FROM IP ADDRESS -------")
        # PARAMETER
        ip_address_string = '216.58.208.142'
        ip_address_string = '20.190.160.130'
        # QUERY
        print(f"Parameter: {ip_address_string}")
        try:
            iae = helper_ip_address.get(ip_address_string)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        try:
            dnes = helper_ip_address.resolve_reversed_access_path(iae, True)
        except DoesNotExist as exc:
            self.fail(f"!!! {str(exc)} !!!")
        for i, dne in enumerate(dnes):
            print(f"domain name[{i+1}/{len(dnes)}]: {dne.string}")
        print(f"------- [1] END QUERY REVERSED ACCESS PATH FROM IP ADDRESS -------")


if __name__ == '__main__':
    unittest.main()
