import ipaddress
import unittest
from utils import network_utils


class IpAddressNetworkTestCase(unittest.TestCase):
    def test_1_from_network(self):
        print(f"\n------- [1] START IS ADDRESS IN NETWORK TEST -------")
        # PARAMETERS
        ip = ipaddress.IPv4Address('216.239.38.10')
        network = ipaddress.IPv4Network('216.239.32.0/19')
        # ELABORATION
        print(f"Parameter IP address: {ip.exploded}")
        print(f"Parameter IP network: {network.compressed}")
        result = network_utils.is_in_network(ip, network)
        print(f"{ip.compressed} is in {network.compressed}? {result}")
        self.assertTrue(result)
        print(f"------- [1] END IS ADDRESS IN NETWORK TEST -------")

    def test_2_from_address_range(self):
        print(f"\n------- [2] START IS ADDRESS IN ADDRESS RANGE TEST -------")
        # PARAMETERS
        ip = ipaddress.IPv4Address('150.145.1.4')
        start_ip_range = ipaddress.IPv4Address('150.145.0.0')
        end_ip_range = ipaddress.IPv4Address('150.146.255.255')
        # ELABORATION
        print(f"Parameter IP address: {ip.exploded}")
        print(f"Parameter start IP address range: {start_ip_range.exploded}")
        print(f"Parameter end IP address range: {end_ip_range.exploded}")
        result = network_utils.is_in_ip_range(ip, start_ip_range, end_ip_range)
        print(f"{ip.compressed} is in [{start_ip_range.compressed} - {end_ip_range.compressed}]? {result}")
        self.assertTrue(result)
        print(f"------- [2] END IS ADDRESS IN ADDRESS RANGE TEST -------")

    def test_3_predefined_network(self):
        print(f"\n------- [3] START GETTING PREDEFINED NETWORK TEST -------")
        # PARAMETERS
        ip = ipaddress.IPv4Address('150.145.1.4')
        # ELABORATION
        print(f"Parameter IP address: {ip.exploded}")
        result = network_utils.get_predefined_network(ip)
        print(f"Predefined network from {ip.compressed}: {result.compressed}")
        print(f"------- [3] END GETTING PREDEFINED NETWORK TEST -------")


if __name__ == '__main__':
    unittest.main()
