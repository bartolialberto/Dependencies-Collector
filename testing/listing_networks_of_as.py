import ipaddress
import unittest
from pathlib import Path
from entities.IpAsDatabase import IpAsDatabase, EntryIpAsDatabase
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError


class ListingNetworkOfAutonomousSystem(unittest.TestCase):
    # All methods inherited: https://docs.python.org/3/library/unittest.html#unittest.TestCase.debug

    @classmethod
    def setUpClass(cls) -> None:
        # eseguito all'inizio di tutti i test UNA volta
        cls.db = IpAsDatabase(project_root_directory=Path.cwd().parent)

    def test_listing_networks_from_ip_address(self):
        # PARAMETERS
        params = ["194.119.192.34", "192.12.94.30", "192.42.177.30", "192.58.128.30"]
        # Actual test
        ip_params = list()
        for param in params:
            ip_params.append(ipaddress.ip_address(param))
        print(f"test_listing_networks_from_ip_address ****************************************************************")
        print(f"ips: {str(ip_params)}")
        for ip in ip_params:
            try:
                entry = self.db.resolve_range(ip)
                try:
                    belonging_network, networks = entry.get_network_of_ip(ip)
                    print(
                        f"For ip: {ip.compressed} as found is AS{entry.as_number} [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. Networks are:")
                    for index, network in enumerate(networks):
                        print(f"---> network[{index + 1}/{len(networks)}]: {network.compressed}")
                    print(f"Belonging network: {belonging_network.compressed}\n")
                except ValueError as f:
                    print(f"!!! {str(f)} !!!")
            except ValueError as e:
                print(f"!!! {str(e)} !!!")

    def test_listing_networks_from_as_number(self):
        # PARAMETERS
        params = [31034]
        # Actual test
        print(f"\ntest_listing_networks_from_as_number ****************************************************************")
        print(f"AS numbers: {str(params)}")
        for param in params:
            try:
                temp = self.db.get_entry_from_as_number(param)
                print(f"--> for AS{str(param)}: {str(temp)}")
            except (ValueError, AutonomousSystemNotFoundError) as e:
                print(f"--> for AS{str(param)}: !!! {str(e)} !!!")


if __name__ == '__main__':
    unittest.main()
