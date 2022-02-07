import ipaddress
import unittest
from pathlib import Path
from entities.resolvers.IpAsDatabase import IpAsDatabase
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from utils import file_utils


class EntryIpAsDatabaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        PRD = file_utils.get_project_root_directory()
        cls.db = IpAsDatabase(project_root_directory=PRD)

    def test_from_ip_addresses(self):
        print(f"\n------- [1] START GETTING NETWORK FROM ENTRY TEST -------")
        # PARAMETERS
        params = ['150.145.1.4']
        # Actual test
        ip_params = list()
        for param in params:
            ip_params.append(ipaddress.ip_address(param))
        print(f"ips: {str(list(map(lambda ip: ip.exploded, ip_params)))}")
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
            except (ValueError, AutonomousSystemNotFoundError) as e:
                print(f"!!! {str(e)} !!!")
        print(f"------- [1] END GETTING NETWORK FROM ENTRY TEST -------")

    def test_from_as_number(self):
        print(f"\n------- [2] START GETTING ENTRY FROM AS NUMBER TEST -------")
        # PARAMETERS
        params = [31034]
        # Actual test
        print(f"AS numbers: {str(params)}")
        for param in params:
            try:
                temp = self.db.get_entry_from_as_number(param)
                print(f"--> for AS{str(param)}: {str(temp)}")
            except (ValueError, AutonomousSystemNotFoundError) as e:
                print(f"--> for AS{str(param)}: !!! {str(e)} !!!")
        print(f"------- [2] END GETTING ENTRY FROM AS NUMBER TEST -------")


if __name__ == '__main__':
    unittest.main()
