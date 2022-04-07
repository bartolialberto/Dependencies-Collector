import unittest
from ipaddress import IPv4Address
from persistence import helper_autonomous_system, helper_ip_address


class GettingAutonomousSystemFromIPAddressQueryCase(unittest.TestCase):
    ase = None
    iae = None
    ip_address = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.ip_address = IPv4Address('156.154.65.196')
        # QUERY
        cls.iae = helper_ip_address.get(cls.ip_address)
        cls.ase = helper_autonomous_system.get_of_ip_address(cls.iae)
        print(f"IP address: {cls.ip_address.exploded} ==> AS{cls.ase.number}")

    def test_01_from_autonomous_system(self):
        print(f"\n------- [1] START QUERY -------")
        iaes = helper_autonomous_system.get_all_ip_addresses_of(self.ase)
        str_iaes = set(map(lambda iae: iae.exploded_notation, iaes))
        print(f"AS{self.ase.number} ==> {str(str_iaes)}")
        self.assertIn(self.ip_address.exploded, str_iaes)
        print(f"------- [1] END QUERY -------")


if __name__ == '__main__':
    unittest.main()
