import unittest
from pathlib import Path
from peewee import DoesNotExist
from entities.DnsResolver import DnsResolver
from entities.TLDPageScraper import TLDPageScraper
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from persistence import helper_domain_name, helper_application_results, helper_nameserver, helper_zone, helper_alias, \
    helper_zone_links


# DOMAIN NAME LIST EXAMPLES
# ['accounts.google.com', 'login.microsoftonline.com', 'www.facebook.com', 'auth.digidentity.eu', 'clave-dninbrt.seg-social.gob.es', 'pasarela.clave.gob.es', 'unipd.it', 'dei.unipd.it', 'units.it']
# ['accounts.google.com', 'login.microsoftonline.com', 'www.facebook.com', 'auth.digidentity.eu', 'clave-dninbrt.seg-social.gob.es', 'pasarela.clave.gob.es']
# ['unipd.it', 'dei.unipd.it', 'www.units.it', 'units.it', 'dia.units.it']
# ['google.it']
# ['ocsp.digicert.com']
# ['modor.verisign.net']
from utils import domain_name_utils


class DnsResolvingIntegrityTestCase(unittest.TestCase):
    """
    Test class that takes a list of domain names and then executes the DNS resolving.
    Finally checks the integrity of the zone dependencies found with what was saved and retrieved from the database.

    """
    import_cache_from_output_folder = None
    dns_resolver = None
    clear_cache_at_start = None
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
        cls.domain_names = ['unipd.it', 'dei.unipd.it', 'www.units.it', 'units.it', 'dia.units.it']
        cls.import_cache_from_output_folder = False
        cls.clear_cache_at_start = False
        cls.consider_tld = False
        # ELABORATION
        cls.PRD = DnsResolvingIntegrityTestCase.get_project_root_folder()
        tlds = TLDPageScraper.import_txt_from_input_folder(cls.PRD)
        cls.dns_resolver = DnsResolver(tlds)
        if cls.clear_cache_at_start:
            cls.dns_resolver.cache.clear()
        if cls.import_cache_from_output_folder:
            try:
                cls.dns_resolver.cache.load_csv_from_output_folder(filename='cache_from_dns_test.csv', project_root_directory=cls.PRD)
            except FilenameNotFoundError as e:
                print(f"!!! {str(e)} !!!")
                exit(1)
        print("START DNS DEPENDENCIES RESOLVER")
        cls.dns_results, cls.zone_dependencies_per_zone, cls.zone_dependencies_per_nameserver, cls.error_logs = cls.results = cls.dns_resolver.resolve_multiple_domains_dependencies(cls.domain_names)
        print("END DNS DEPENDENCIES RESOLVER")
        print("INSERTION INTO DATABASE... ", end='')
        try:
            helper_application_results.insert_dns_result(cls.results)
        except InvalidDomainNameError as e:
            print(f"!!! {str(e)} !!!")
            exit(0)
        print("DONE")

    def test_1_domain_names_integrity(self):
        """
        Checks data integrity between input domain names and domain name entities saved in the DB.

        """
        print("\n------- [1] START DOMAIN NAMES INTEGRITY CHECK -------")
        db_domain_names = set()
        domain_names_with_trailing_point = set()
        for domain_name in self.domain_names:
            domain_names_with_trailing_point.add(domain_name_utils.insert_trailing_point(domain_name))
        for domain_name in domain_names_with_trailing_point:
            try:
                dne = helper_domain_name.get(domain_name)
                db_domain_names.add(dne.name)
            except DoesNotExist as e:
                print(f"!!! {str(e)} !!!")
        self.assertSetEqual(domain_names_with_trailing_point, db_domain_names)
        print(f"Reached this print means everything went well")
        print("------- [1] END DOMAIN NAMES INTEGRITY CHECK -------")

    def test_2_nameservers_integrity(self):
        """
        Checks data integrity between nameservers retrieved from elaboration and nameservers entities saved in the DB.

        """
        print("\n------- [2] START NAMESERVERS INTEGRITY CHECK -------")
        count_assertions = 0
        for domain_name in self.dns_results.keys():
            for zone in self.dns_results[domain_name]:
                # check presence in the db
                for nameserver in zone.nameservers:
                    try:
                        nse, dne = helper_nameserver.get(nameserver.name)
                    except DoesNotExist as e:
                        print(f"!!! {str(e)} !!!")

                # check they are the same
                nameservers_result_set = set(map(lambda rr: rr.name, zone.nameservers))
                tmp = helper_nameserver.get_from_zone_name(zone.name)
                nameservers_db_set = set(map(lambda x: x.name.name, tmp))
                self.assertSetEqual(nameservers_result_set, nameservers_db_set)
                count_assertions = count_assertions + 1
        print(f"Reached this print means everything went well ({count_assertions} assertions)")
        print("------- [2] END NAMESERVERS INTEGRITY CHECK -------")

    def test_3_aliases_integrity(self):
        """
        Checks data integrity between aliases retrieved from elaboration and aliases relations saved in the DB.

        """
        print("\n------- [3] START ALIASES INTEGRITY CHECK -------")
        """
        for domain_name in self.dns_results.keys():
            for zone in self.dns_results[domain_name]:
                for alias in zone.aliases:
                    try:
                        dne_set = helper_alias.get_all_aliases_from_name(alias.name)
                    except DoesNotExist as e:
                        print(f"!!! {str(e)} !!!")
                        continue
                    dne_name_set = set(map(lambda rr: rr.name, dne_set))

                    if alias.get_first_value() in dne_name_set:
                        pass
                    else:
                        raise ValueError
        """

        count_assertions = 0
        for domain_name in self.dns_results.keys():
            for zone in self.dns_results[domain_name]:
                for alias in zone.aliases:
                    try:
                        dnes = helper_alias.get_all_aliases_from_name(alias.name)
                    except DoesNotExist as e:
                        print(f"!!! {str(e)} !!!")
                        continue
                    dnes_names = set(map(lambda dne: dne.name, dnes))
                    self.assertIn(alias.get_first_value(), dnes_names)
                    count_assertions = count_assertions + 1
        print(f"Reached this print means everything went well ({count_assertions} assertions)")
        print("------- [3] END ALIASES INTEGRITY CHECK -------")

    def test_4_TLD_presence(self):
        """
        Checks if are there TLD zones saved in the DB according to the boolean parameter of this test class.

        """
        print("\n------- [4] START TLD PRESENCE CHECK -------")
        tld_in_database = set()
        if not self.consider_tld:
            zes = helper_zone.get_all()
            for i, ze in enumerate(zes):
                if ze.name in self.dns_resolver.tld_list:
                    print(f"[{i + 1}/{len(zes)}] = {str(ze)} is in database")
                    tld_in_database.add(ze.name)
                else:
                    pass
        self.assertSetEqual(set(), tld_in_database)
        print(f"Reached this print means everything went well")
        print("------- [4] END TLD PRESENCE CHECK -------")

    def test_5_dns_results_integrity_check(self):
        """
        Checks data integrity between zone dependencies of input domain names retrieved from elaboration, and DB
        relations corresponding to zone dependencies between domain names and zones.

        """
        print("\n------- [5] START DNS RESULTS INTEGRITY CHECK -------")
        count_assertions = 0
        for i, domain_name in enumerate(self.dns_results.keys()):
            try:
                zones_set_db = helper_zone.get_zone_dependencies_of(domain_name)
            except DoesNotExist as e:
                print(f"!!! {str(e)} !!!")
                continue
            are_same_len = len(self.dns_results[domain_name]) == len(zones_set_db)
            print(f"Results length comparison: from elaboration={len(self.dns_results[domain_name])}, from db={len(zones_set_db)}, are equal? {are_same_len}")
            if not are_same_len:
                print(f"Tot zone dependencies for '{domain_name}':")
                print(f"--> number of zone dependencies found from elaboration: {len(self.dns_results[domain_name])}")
                for j, zone in enumerate(self.dns_results[domain_name]):
                    print(f"----> zone[{j+1}/{len(self.dns_results[domain_name])}] = {zone.name}")
                print(f"--> number of zone dependencies found from db: {len(zones_set_db)}")
                for j, ze in enumerate(zones_set_db):
                    print(f"----> zone[{j+1}/{len(zones_set_db)}] = {ze.name}")
            self.assertEqual(len(self.dns_results[domain_name]), len(zones_set_db))
            count_assertions = count_assertions + 1
        print(f"Reached this print means everything went well ({count_assertions} assertions)")
        print("------- [5] END DNS RESULTS INTEGRITY CHECK -------")

    def test_6_zone_dependencies_per_nameserver_integrity_check(self):
        """
        Checks data integrity between zone dependencies of nameservers retrieved from elaboration, and DB relations
        corresponding to zone dependencies between nameservers and zones.

        """
        count_assertions = 0
        print("\n------- [6] START ZONE DEPENDENCIES PER NAMESERVER INTEGRITY CHECK -------")
        for i, nameserver in enumerate(self.zone_dependencies_per_nameserver.keys()):
            try:
                zones_set_db = helper_zone.get_zone_dependencies_of(nameserver)
            except DoesNotExist as e:
                print(f"!!! {str(e)} !!!")
                continue
            are_same_len = len(self.zone_dependencies_per_nameserver[nameserver]) == len(zones_set_db)
            print(f"Results length comparison: from elaboration={len(self.zone_dependencies_per_nameserver[nameserver])}, from db={len(zones_set_db)}, are equal? {are_same_len}")
            if not are_same_len:
                print(f"Tot zone dependencies for '{nameserver}':")
                print(f"--> number of zone dependencies found from elaboration: {len(self.zone_dependencies_per_nameserver[nameserver])}")
                for j, zone_name in enumerate(self.zone_dependencies_per_nameserver[nameserver]):
                    print(f"----> zone[{j + 1}/{len(self.zone_dependencies_per_nameserver[nameserver])}] = {zone_name}")
                print(f"--> number of zone dependencies found from db: {len(zones_set_db)}")
                for j, ze in enumerate(zones_set_db):
                    print(f"----> zone[{j + 1}/{len(zones_set_db)}] = {ze.name}")
            self.assertEqual(len(self.zone_dependencies_per_nameserver[nameserver]), len(zones_set_db))
            count_assertions = count_assertions + 1
        print(f"Reached this print means everything went well ({count_assertions} assertions)")
        print("------- [6] END ZONE DEPENDENCIES PER NAMESERVER INTEGRITY CHECK -------")

    def test_7_zone_dependencies_per_zone_integrity_check(self):
        """
        Checks data integrity between zone dependencies of zones retrieved from elaboration, and DB relations
        corresponding to zone dependencies between zones.

        """
        count_assertions = 0
        print("\n------- [7] START ZONE DEPENDENCIES PER ZONE INTEGRITY CHECK -------")
        for i, zone in enumerate(self.zone_dependencies_per_zone.keys()):
            try:
                ze_set_db = helper_zone_links.get_all_from_zone_name(zone)
            except DoesNotExist as e:
                print(f"!!! {str(e)} !!!")
                continue
            are_same_len = len(self.zone_dependencies_per_zone[zone]) == len(ze_set_db)
            print(f"Results length comparison: from elaboration={len(self.zone_dependencies_per_zone[zone])}, from db={len(ze_set_db)}, are equal? {are_same_len}")
            if not are_same_len:
                print(f"Tot zone dependencies for '{zone}':")
                print(f"--> number of zone dependencies found from elaboration: {len(self.zone_dependencies_per_zone[zone])}")
                for j, zone_name in enumerate(self.zone_dependencies_per_zone[zone]):
                    print(f"----> zone[{j + 1}/{len(self.zone_dependencies_per_zone[zone])}] = {zone_name}")
                print(f"--> number of zone dependencies found from db: {len(ze_set_db)}")
                for j, ze in enumerate(ze_set_db):
                    print(f"----> zone[{j + 1}/{len(ze_set_db)}] = {ze.name}")
            self.assertEqual(len(self.zone_dependencies_per_zone[zone]), len(ze_set_db))
            count_assertions = count_assertions + 1
        print(f"Reached this print means everything went well ({count_assertions} assertions)")
        print("------- [7] END ZONE DEPENDENCIES PER ZONE INTEGRITY CHECK -------")


if __name__ == '__main__':
    unittest.main()
