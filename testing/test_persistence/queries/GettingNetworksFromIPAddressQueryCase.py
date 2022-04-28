import unittest
from ipaddress import IPv4Address
from persistence import helper_ip_address, helper_ip_network, helper_ip_range_tsv, helper_ip_range_rov


class GettingNetworksFromIPAddressQueryCase(unittest.TestCase):
    irre = None
    irte = None
    ine = None
    iae = None
    ip_address = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.ip_address = IPv4Address('156.154.65.196')
        # ELABORATION
        cls.iae = helper_ip_address.get(cls.ip_address)
        cls.ine = helper_ip_network.get_of(cls.iae)
        cls.irte = helper_ip_range_tsv.get_of(cls.iae)
        cls.irre = helper_ip_range_rov.get_of(cls.iae)
        print(f"IP address: {cls.ip_address.exploded} ==> IP network: {cls.ine.compressed_notation}")
        if cls.irte is None:
            print(f"IP address: {cls.ip_address.exploded} ==> IP range TSV: null")
        else:
            print(f"IP address: {cls.ip_address.exploded} ==> IP range TSV: {cls.irte.compressed_notation}")
        if cls.irre is None:
            print(f"IP address: {cls.ip_address.exploded} ==> IP range ROV: null")
        else:
            print(f"IP address: {cls.ip_address.exploded} ==> IP range ROV: {cls.irre.compressed_notation}")

    def test_01_from_network(self):
        print(f"\n------- START QUERY 1 -------")
        iaes = helper_ip_network.get_all_addresses_of(self.ine)
        addresses = set(map(lambda iae: iae.exploded_notation, iaes))
        print(f"{self.ine.compressed_notation} ==> {str(addresses)}")
        self.assertIn(self.ip_address.exploded, addresses)
        print(f"------- END QUERY 1 -------")

    def test_02_from_range_tsv(self):
        if self.irte is None:
            self.skipTest('IP range TSV is None.')
        print(f"\n------- START QUERY 2 -------")
        iaes = helper_ip_range_tsv.get_all_addresses_of(self.irte)
        addresses = set(map(lambda iae: iae.exploded_notation, iaes))
        print(f"{self.irte.compressed_notation} ==> {str(addresses)}")
        self.assertIn(self.ip_address.exploded, addresses)
        print(f"------- END QUERY 2 -------")

    def test_03_from_range_rov(self):
        if self.irre is None:
            self.skipTest('IP range ROV is None.')
        print(f"\n------- START QUERY 3 -------")
        iaes = helper_ip_range_rov.get_all_addresses_of(self.irre)
        addresses = set(map(lambda iae: iae.exploded_notation, iaes))
        print(f"{self.irre.compressed_notation} ==> {str(addresses)}")
        self.assertIn(self.ip_address.exploded, addresses)
        print(f"------- END QUERY 3 -------")


if __name__ == '__main__':
    unittest.main()
