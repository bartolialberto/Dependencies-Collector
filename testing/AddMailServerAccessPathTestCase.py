import ipaddress
import unittest
from pathlib import Path
from peewee import DoesNotExist
from entities.resolvers.DnsResolver import DnsResolver
from entities.resolvers.IpAsDatabase import IpAsDatabase
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.UnknownReasonError import UnknownReasonError
from persistence import helper_mail_server, helper_domain_name, helper_access, helper_ip_address, helper_ip_network, \
    helper_ip_address_depends, helper_ip_range_tsv, helper_alias, helper_autonomous_system, helper_network_numbers
from persistence.BaseModel import project_root_directory_name


class AddMailServerAccessPathTestCase(unittest.TestCase):
    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == project_root_directory_name:
                return current
            else:
                current = current.parent

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        consider_tld = False
        # SET UP
        PRD = AddMailServerAccessPathTestCase.get_project_root_folder()
        cls.dns_resolver = DnsResolver(consider_tld)
        cls.as_database = IpAsDatabase(project_root_directory=PRD)

    def test_addition(self):
        mses = helper_mail_server.get_everyone()
        for mse in mses:
            try:
                rr_a, rr_cnames = self.dns_resolver.resolve_access_path(mse.name.string)
            except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
                try:
                    aa = helper_access.get_of_entity_domain_name(mse.name)
                except DoesNotExist:
                    helper_access.insert(mse.name, None)
                continue
            # cnames
            last_dne = mse.name
            for rr in rr_cnames:
                name = helper_domain_name.insert(rr.name)
                alias = helper_domain_name.insert(rr.get_first_value())
                helper_alias.insert(name, alias)
                last_dne = alias
            # answer
            for value in rr_a.values:
                iae = helper_ip_address.insert(value)
                ine = helper_ip_network.insert_from_address_entity(iae)
                helper_access.insert(last_dne, iae)
                # IP address depends
                ip = ipaddress.IPv4Address(value)
                try:
                    entry = self.as_database.resolve_range(ip)
                except (ValueError, AutonomousSystemNotFoundError):
                    continue
                try:
                    ip_range_tsv, networks = entry.get_network_of_ip(ip)
                except (TypeError, ValueError):
                    helper_ip_address_depends.insert(iae, ine, None, None)
                    continue
                irte = helper_ip_range_tsv.insert(ip_range_tsv.compressed)
                helper_ip_address_depends.insert(iae, ine, irte, None)
                ase = helper_autonomous_system.insert(entry.as_number, entry.as_description)
                helper_network_numbers.insert(irte, ase)

    def test_prints(self):
        mses = helper_mail_server.get_everyone()
        count_unresolved = 0
        for i, mse in enumerate(mses):
            try:
                iaes, dnes = helper_domain_name.resolve_access_path(mse.name, get_only_first_address=False)
                iaes_string = set(map(lambda iae: iae.exploded_notation, iaes))
                print(f"[{i+1}/{len(mses)}] {mse.name.string} ==> {str(iaes_string)}")
            except (DoesNotExist, NoAvailablePathError) as e:
                print(f"!!! {str(e)} !!!")
                count_unresolved = count_unresolved + 1
        print(f"UNRESOLVED = {count_unresolved}")


if __name__ == '__main__':
    unittest.main()
