import unittest
from pathlib import Path
import dns.resolver
from dns.name import Name
from peewee import DoesNotExist
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_zone, helper_name_server, helper_domain_name, helper_ip_network
from utils import file_utils, network_utils


class CheckExceedingNameserversWithRespectToNetworksTestCase(unittest.TestCase):
    """ Put the exceeding_zone.csv file in the input folder """
    networks = None
    nameservers = None
    zone_names = None

    @classmethod
    def setUpClass(cls) -> None:
        PRD = file_utils.get_project_root_directory()
        try:
            files_result = file_utils.search_for_filename_in_subdirectory('input', 'exceeding_zone.csv', PRD)
        except FilenameNotFoundError:
            raise
        file = files_result[0]
        cls.nameservers = dict()
        cls.networks = dict()
        cls.zone_names = list()
        f = open(file, "r")
        for i, line in enumerate(f):
            if i != 0:
                # split_line[0] is row index
                split_line = line.split(',')
                cls.zone_names.append(split_line[1])
                cls.nameservers[split_line[1]] = int(split_line[2])
                cls.networks[split_line[1]] = int(split_line[3])
        f.close()
        cls.zone_names.pop(0)

    def test_check_exceeding(self):
        dns_resolver = dns.resolver.Resolver()
        count_exceeding_zones = 0
        db_zone_names = list()
        for i, zone_name in enumerate(self.zone_names):
            try:
                ze = helper_zone.get(zone_name)
            except DoesNotExist:
                raise
            print(f"zone[{i+1}/{len(self.zone_names)}]: {zone_name}  (#nameservers={self.nameservers[zone_name]} VS. #networks={self.networks[zone_name]})")

            # from DB
            try:
                nses = helper_name_server.get_all_from_zone_entity(ze)
            except DoesNotExist:
                raise
            db_ines = set()
            for nse in nses:
                try:
                    iaes, path_dnes = helper_domain_name.resolve_access_path(nse.name, get_only_first_address=False)
                except (DoesNotExist, NoAvailablePathError):
                    raise
                for iae in iaes:
                    ine = helper_ip_network.get_of(iae)
                    db_ines.add(ine)

            # from DNS queries
            name_servers = list()
            addresses = list()
            query_ines = set()
            answer = dns_resolver.resolve(zone_name, 'NS')
            for val in answer:
                if isinstance(val, Name):
                    name_servers.append(str(val))
                else:
                    name_servers.append(val.to_text())
            for name_server in name_servers:
                answer = dns_resolver.resolve(name_server, 'A')
                for val in answer:
                    if isinstance(val, Name):
                        addresses.append(str(val))
                    else:
                        addresses.append(val.to_text())
            for address in addresses:
                ine = network_utils.get_predefined_network(address)
                query_ines.add(ine)

            print(f"--->  DB : (#nameservers={len(nses)} VS. #networks={len(db_ines)})")
            print(f"--->QUERY:(#nameservers={len(name_servers)} VS. #networks={len(query_ines)})")
            if len(db_ines) > len(nses):
                count_exceeding_zones = count_exceeding_zones + 1
                db_zone_names.append(zone_name)
            else:
                pass
        self.assertSetEqual(set(self.zone_names), set(db_zone_names))


if __name__ == '__main__':
    unittest.main()
