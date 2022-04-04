import unittest
from peewee import DoesNotExist
from persistence import helper_ip_address, helper_ip_address_depends, helper_ip_network
from utils import network_utils


class IpDependenciesErrorSimulationTestCase(unittest.TestCase):
    def test_01_set_ip_range_tsv_to_null(self):
        print(f"\n------- [1] START SETTING IP RANGE TSV TO NULL QUERY -------")
        # PARAMETERS
        for_ip_address = '216.58.209.46'
        # ELABORATION
        try:
            iae = helper_ip_address.get(for_ip_address)
        except DoesNotExist:
            iae = helper_ip_address.insert(for_ip_address)
        try:
            iada = helper_ip_address_depends.get_from_entity_ip_address(iae)
            iada.ip_range_tsv = None
            iada.ip_range_rov = None
            iada.save()
        except DoesNotExist:
            net = network_utils.get_predefined_network(for_ip_address)
            ine = helper_ip_network.insert(net)
            helper_ip_address_depends.insert(iae, ine, None, None)
        print(f"------- [1] END SETTING IP RANGE TSV TO NULL QUERY -------")

    def test_02_set_ip_range_rov_to_null(self):
        print(f"\n------- [2] START SETTING IP RANGE ROV TO NULL QUERY -------")
        # PARAMETERS
        for_ip_address = '216.58.209.46'
        # ELABORATION
        try:
            iae = helper_ip_address.get(for_ip_address)
        except DoesNotExist:
            iae = helper_ip_address.insert(for_ip_address)
        try:
            iada = helper_ip_address_depends.get_from_entity_ip_address(iae)
            iada.ip_range_rov = None
            iada.save()
        except DoesNotExist:
            net = network_utils.get_predefined_network(for_ip_address)
            ine = helper_ip_network.insert(net)
            helper_ip_address_depends.insert(iae, ine, None, None)
        print(f"------- [2] END SETTING IP RANGE ROV TO NULL QUERY -------")


if __name__ == '__main__':
    unittest.main()
