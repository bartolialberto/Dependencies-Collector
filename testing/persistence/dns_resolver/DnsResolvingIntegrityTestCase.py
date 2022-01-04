import os
import unittest
from pathlib import Path
from typing import List
from entities.DnsResolver import DnsResolver
from entities.TLDPageScraper import TLDPageScraper
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from persistence import helper_domain_name, helper_application_results, helper_nameserver, helper_zone, helper_alias


class DnsResolvingIntegrityTestCase(unittest.TestCase):
    """
    Test class that takes a list of domain names and then executes the DNS resolving.
    Finally checks the integrity of the zone dependencies found with what was saved and retrieved from the database.

    """
    domain_names = None
    results = None
    PRD = None
    domain_name_list = None

    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == 'LavoroTesi':
                return current
            else:
                current = current.parent

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        # cls.domain_names = ['accounts.google.com', 'login.microsoftonline.com', 'www.facebook.com', 'auth.digidentity.eu', 'clave-dninbrt.seg-social.gob.es', 'pasarela.clave.gob.es']
        # cls.domain_names = ['unipd.it', 'units.it', 'dei.unipd.it', 'ocsp.digicert.com', 'lorenzo.fabbio@unipd.it', 'studente110847@dei.unipd.it']
        cls.domain_names = ['unipd.it', 'dei.unipd.it']
        # cls.domain_names = ['ocsp.digicert.com']
        # cls.domain_names = ['modor.verisign.net']
        # ELABORATION
        cls.PRD = DnsResolvingIntegrityTestCase.get_project_root_folder()
        tlds = TLDPageScraper.import_txt_from_input_folder(cls.PRD)
        dns_resolver = DnsResolver(tlds)

        dns_resolver.cache.clear()

        """
        try:
            cls.dns_resolver.cache.load_csv_from_output_folder(filename='cache_from_dns_test.csv', project_root_directory=cls.PRD)
        except FilenameNotFoundError:
            pass
        """
        print("START DNS DEPENDENCIES RESOLVER")
        cls.dns_results, cls.zone_dependencies, cls.nameservers, cls.error_logs = cls.results = dns_resolver.resolve_multiple_domains_dependencies(cls.domain_names)
        print("END DNS DEPENDENCIES RESOLVER")
        print("START CACHE DNS DEPENDENCIES RESOLVER")
        cls.dns_new_results, cls.zone_new_dependencies, cls.new_nameservers, cls.error_new_logs = dns_resolver.resolve_multiple_domains_dependencies(cls.domain_names)
        print("END CACHE DNS DEPENDENCIES RESOLVER")
        print("INSERTION INTO DATABASE... ", end='')
        helper_application_results.insert_dns_result(cls.results)
        print("DONE")

    def test_1_domain_names_integrity(self):
        print("\nSTART DOMAIN NAMES INTEGRITY CHECK")
        db_domain_names = list()
        for domain_name in self.domain_names:
            dne = helper_domain_name.get(domain_name)
            db_domain_names.append(dne.name)
        self.assertListEqual(self.domain_names, db_domain_names)
        print("END DOMAIN NAMES INTEGRITY CHECK")

    def test_2_nameservers_integrity(self):
        print("\nSTART NAMESERVERS INTEGRITY CHECK")
        for domain_name in self.dns_results.keys():
            for zone in self.dns_results[domain_name]:
                # check presence in the db
                for nameserver in zone.nameservers:
                    nse, dne = helper_nameserver.get(nameserver.name)

                # check they are the same
                nameservers_result_set = set(map(lambda rr: rr.name, zone.nameservers))
                tmp = helper_nameserver.get_from_zone_name(zone.name)
                nameservers_db_set = set(map(lambda x: x.name.name, tmp))
                self.assertSetEqual(nameservers_result_set, nameservers_db_set)
        print("END NAMESERVERS INTEGRITY CHECK")

    def test_3_aliases_integrity(self):
        print("\nSTART ALIASES INTEGRITY CHECK")
        for domain_name in self.dns_results.keys():
            for zone in self.dns_results[domain_name]:
                for alias in zone.aliases:
                    tmp = helper_alias.get_all_aliases_from_name(alias.name)
                    dne_set = set(map(lambda rr: rr.name, tmp))

                    if alias.get_first_value() in dne_set:
                        pass
                    else:
                        raise ValueError
        print("END ALIASES INTEGRITY CHECK")

    '''
    def test_integrity(self):
        print("\nSTART INTEGRITY CHECK")
        for i, domain_name in enumerate(self.results.keys()):
            list_zones = helper_domain_name.get_zone_dependencies(domain_name)
            self.assertEqual(len(self.results[domain_name]), len(list_zones))
            print(f"Tot zone dependencies for '{domain_name}':")
            print(f"--> number of zone dependencies found from elaboration: {len(self.results[domain_name])}")
            for j, zone in enumerate(self.results[domain_name]):
                print(f"----> number of nameservers of zone[{j+1}/{len(self.results[domain_name])}] '{zone.name}' from elaboration is: {len(zone.nameservers)}")
            print(f"--> number of zone dependencies found in the database: {len(list_zones)}")
            for j, zone in enumerate(list_zones):
                print(f"----> number of nameservers of zone[{j+1}/{len(list_zones)}] '{zone.name}' from database is: {len(zone.nameservers)}")
            # integrity test
            for z in self.results[domain_name]:
                try:
                    list_zones.remove(z)   # needs an overwritten __eq__ method in Zone class
                except ValueError:
                    print(f"!!! There's a zone dependency from elaboration not present in the database: {str(z)} !!!")
            # for every zone dependency of the elaboration, it is removed from the list (of zone dependencies) retrieved
            # from the database. So in the end, if everything is correct, the list should be empty.
            self.assertEqual(0, len(list_zones))
            print("")
        print("END INTEGRITY CHECK")
    '''


if __name__ == '__main__':
    unittest.main()
