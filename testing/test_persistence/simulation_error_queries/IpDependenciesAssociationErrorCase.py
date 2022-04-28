import unittest
from ipaddress import IPv4Address
from peewee import DoesNotExist
from persistence import helper_ip_address, helper_ip_address_depends, helper_ip_network
from utils import network_utils


class IpDependenciesAssociationErrorCase(unittest.TestCase):
    def test_01_set_ip_range_tsv_to_null(self):
        print(f"\n------- START TEST 1 -------")
        # PARAMETERS
        for_ip_address = IPv4Address('216.58.209.46')
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
        print(f"------- END TEST 1 -------")

    def test_02_set_ip_range_rov_to_null(self):
        print(f"\n------- START TEST 2 -------")
        # PARAMETERS
        for_ip_address = IPv4Address('216.58.209.46')
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
        print(f"------- END TEST 1 -------")


if __name__ == '__main__':
    unittest.main()
