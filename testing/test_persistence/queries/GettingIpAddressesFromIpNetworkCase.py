import unittest
from ipaddress import IPv4Network
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_ip_network


class GettingAutonomousSystemFromIPAddressQueryCase(unittest.TestCase):
    ine = None
    ip_network = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.ip_network = IPv4Network('103.49.80.0/24')
        # QUERY
        cls.ine = helper_ip_network.get(cls.ip_network)
        print(f"IP network: {cls.ip_network.compressed}")

    def test_01_printing_result(self):
        print(f"\n------- START QUERY 1 -------")
        try:
            iaes = helper_ip_network.get_all_addresses_of(self.ine)
        except NoDisposableRowsError as e:
            self.fail(f"!!! {str(e)} !!!")
        for i, iae in enumerate(iaes):
            print(f"address[{i+1}/{len(iaes)}]: {iae.exploded_notation}")
        print(f"------- END QUERY 1 -------")


if __name__ == '__main__':
    unittest.main()
