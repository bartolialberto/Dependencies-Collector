import copy
import ipaddress
import unittest
from peewee import DoesNotExist
from persistence import helper_domain_name, helper_access, helper_ip_address, helper_ip_address_depends


class IpDependenciesErrorSimulationTestCase(unittest.TestCase):
    def test_1_set_access_association_to_null(self):
        print(f"\n------- [1] START SETTING ACCESS ASSOCIATION TO NULL QUERY -------")
        # PARAMETERS
        domain_name = 'www.youtube.com'
        # ELABORATION
        print(f"Domain name: {domain_name}")
        try:
            dne = helper_domain_name.get(domain_name)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        helper_access.delete_of_entity_domain_name(dne)
        helper_access.insert(dne, None)
        print(f"------- [1] END SETTING ACCESS ASSOCIATION TO NULL QUERY -------")

    def test_2_set_ip_address_association_to_null(self):
        print(f"\n------- [2] START SETTING ACCESS ASSOCIATION TO NULL QUERY -------")
        # PARAMETERS
        ip_address_parameter = '216.58.209.46'
        set_ip_range_tsv_to_null = True
        set_ip_range_rov_to_null = True
        # ELABORATION
        ip_address = ipaddress.IPv4Address(ip_address_parameter).exploded
        print(f"IP address: {ip_address}")
        try:
            iae = helper_ip_address.get(ip_address)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        iada = helper_ip_address_depends.get_from_entity_ip_address(iae)
        old_ip_network = copy.deepcopy(iada.ip_network)
        old_ip_range_tsv = copy.deepcopy(iada.ip_range_tsv)
        old_ip_range_rov = copy.deepcopy(iada.ip_range_rov)
        iada.delete_instance()
        if set_ip_range_rov_to_null and set_ip_range_tsv_to_null:
            helper_ip_address_depends.insert(iae, old_ip_network, None, None)
        elif set_ip_range_tsv_to_null:
            helper_ip_address_depends.insert(iae, old_ip_network, old_ip_range_tsv, None)
        elif set_ip_range_rov_to_null:
            helper_ip_address_depends.insert(iae, old_ip_network, None, set_ip_range_rov_to_null)
        else:
            helper_ip_address_depends.insert(iae, old_ip_network, old_ip_range_tsv, old_ip_range_rov)
        print(f"------- [2] END SETTING ACCESS ASSOCIATION TO NULL QUERY -------")


if __name__ == '__main__':
    unittest.main()
