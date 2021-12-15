import ipaddress
import unittest
from utils import network_utils


class MyTestCase(unittest.TestCase):
    def test_from_network(self):
        ip = ipaddress.IPv4Address('216.239.38.10')
        network = ipaddress.IPv4Network('216.239.32.0/19')
        result = network_utils.is_in_network(ip, network)
        print(f"{ip.compressed} is in {network.compressed}? {result}")

    def test_from_address_range(self):
        ip = ipaddress.IPv4Address('150.145.1.4')
        start_ip_range = ipaddress.IPv4Address('150.145.0.0')
        end_ip_range = ipaddress.IPv4Address('150.146.255.255')
        result = network_utils.is_in_ip_range(ip, start_ip_range, end_ip_range)
        print(f"{ip.compressed} is in [{start_ip_range.compressed} - {end_ip_range.compressed}]? {result}")


if __name__ == '__main__':
    unittest.main()
