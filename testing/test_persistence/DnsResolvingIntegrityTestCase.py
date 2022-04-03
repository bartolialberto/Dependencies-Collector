import unittest
from peewee import DoesNotExist
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.DomainName import DomainName
from persistence import helper_domain_name, helper_name_server, helper_zone, helper_alias, helper_alias_to_zone, \
    helper_application_results
from utils import file_utils


# DOMAIN NAME LIST EXAMPLES
# ['cdn-auth.digidentity.eu.', 'twitter.com', 'accounts.google.com', 'login.microsoftonline.com', 'www.facebook.com', 'auth.digidentity.eu', 'clave-dninbrt.seg-social.gob.es', 'pasarela.clave.gob.es', 'unipd.it', 'dei.unipd.it', 'units.it']
# ['google.it']
# ['ocsp.digicert.com']
# ['modor.verisign.net']
class DnsResolvingIntegrityTestCase(unittest.TestCase):
    """
    Test class that takes a list of domain names and then executes the DNS resolving.
    Finally checks the integrity of the zone dependencies found with what was saved and retrieved from the database.

    """
    dns_results = None
    domain_names = None
    resolvers = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_names = [
            DomainName('cdn-auth.digidentity.eu.'),
            DomainName('twitter.com'),
            DomainName('accounts.google.com'),
            DomainName('login.microsoftonline.com'),
            DomainName('www.facebook.com'),
            DomainName('auth.digidentity.eu'),
            DomainName('clave-dninbrt.seg-social.gob.es'),
            DomainName('pasarela.clave.gob.es'),
            DomainName('unipd.it'),
            DomainName('dei.unipd.it'),
            DomainName('units.it')
        ]
        cls.domain_names = [
            DomainName('cdn-auth.digidentity.eu.')
        ]
        consider_tld = True
        # ELABORATION
        execute_script_resolving = False
        execute_rov_scraping = False
        take_snapshot = False
        PRD = file_utils.get_project_root_directory()
        cls.resolvers = ApplicationResolversWrapper(consider_tld, execute_script_resolving, execute_rov_scraping, PRD, take_snapshot)
        cls.dns_results = cls.resolvers.do_dns_resolving(cls.domain_names)
        print(f"\nInsertion into database... ", end='')
        helper_application_results.insert_dns_result(cls.dns_results)
        print(f"DONE.")

    def test_01_input_domain_names_presence(self):
        """
        Checks data integrity between input domain names and domain name entities saved in the DB.

        """
        print("\n------- [1] START INPUT DOMAIN NAMES PRESENCE CHECK -------")
        for domain_name in self.dns_results.zone_dependencies_per_domain_name.keys():
            try:
                dne = helper_domain_name.get(domain_name)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
        print("------- [1] END INPUT DOMAIN NAMES PRESENCE CHECK -------")

    def test_02_nameservers_presence(self):
        """
        Checks data integrity between nameservers retrieved from elaboration and nameservers entities saved in the DB.

        """
        print("\n------- [2] START NAMESERVERS PRESENCE CHECK -------")
        for name_server in self.dns_results.zone_dependencies_per_name_server.keys():
            try:
                nse = helper_name_server.get(name_server)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
        print("------- [2] END NAMESERVERS PRESENCE CHECK -------")

    def test_03_zone_presence(self):
        """
        Checks data integrity between nameservers retrieved from elaboration and nameservers entities saved in the DB.

        """
        print("\n------- [2] START ZONES PRESENCE CHECK -------")
        for zone in self.dns_results.zone_dependencies_per_zone.keys():
            try:
                ze = helper_zone.get(zone.name)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
        print("------- [2] END ZONES PRESENCE CHECK -------")

    def test_04_TLD_presence(self):
        """
        Checks if are there TLD zones saved in the DB according to the boolean parameter of this test class.

        """
        print("\n------- [4] START TLD PRESENCE CHECK -------")
        tld_in_database = set()
        if not self.resolvers.consider_tld:
            zes = helper_zone.get_everyone()
            for ze in zes:
                tmp = DomainName(ze.name)
                if tmp.is_tld():
                    tld_in_database.add(ze)
        self.assertSetEqual(set(), tld_in_database)
        print("------- [4] END TLD PRESENCE CHECK -------")


    def test_05_domain_name_zone_dependencies_integrity(self):
        """
        Checks data integrity between zone dependencies of input domain names retrieved from elaboration, and DB
        relations corresponding to zone dependencies between domain names and zones.

        """
        print("\n------- [5] START DOMAIN NAME ZONE DEPENDENCIES TEST -------")
        print(f"{len(self.dns_results.zone_dependencies_per_domain_name.keys())} input domain names in total")
        for domain_name in self.dns_results.zone_dependencies_per_domain_name.keys():
            zones = self.dns_results.zone_dependencies_per_domain_name[domain_name]
            try:
                zes = helper_zone.get_zone_dependencies_of_domain_name(domain_name)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            str_from_elaboration = set(map(lambda zone: zone.name.string, zones))
            str_from_database = set(map(lambda ze: ze.name, zes))
            self.assertSetEqual(str_from_elaboration, str_from_database)
        print("------- [5] END DOMAIN NAME ZONE DEPENDENCIES TEST -------")

    def test_06_name_server_zone_dependencies(self):
        """
        Checks data integrity between zone dependencies of nameservers retrieved from elaboration, and DB relations
        corresponding to zone dependencies between nameservers and zones.

        """
        print("\n------- [6] START NAMESERVER ZONE DEPENDENCIES TEST -------")
        print(f"{len(self.dns_results.zone_dependencies_per_name_server.keys())} nameservers in total")
        for name_server in self.dns_results.zone_dependencies_per_name_server.keys():
            zones = self.dns_results.zone_dependencies_per_name_server[name_server]
            try:
                zes = helper_zone.get_zone_dependencies_of_domain_name(name_server)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            str_from_elaboration = set(map(lambda zone: zone.name.string, zones))
            str_from_database = set(map(lambda ze: ze.name, zes))
            self.assertSetEqual(str_from_elaboration, str_from_database)
        print("------- [6] END NAMESERVER ZONE DEPENDENCIES TEST -------")

    def test_07_zone_dependencies_per_zone_integrity_check(self):
        """
        Checks data integrity between zone dependencies of zones retrieved from elaboration, and DB relations
        corresponding to zone dependencies between zones.

        """
        print("\n------- [7] START ZONES ZONE DEPENDENCIES TEST -------")
        print(f"{len(self.dns_results.zone_dependencies_per_zone.keys())} zones in total")
        for zone in self.dns_results.zone_dependencies_per_zone.keys():
            zones = self.dns_results.zone_dependencies_per_zone[zone]
            try:
                zes = helper_zone.get_zone_dependencies_of_zone_name(zone.name)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            str_from_elaboration = set(map(lambda zone: zone.name.string, zones))
            str_from_database = set(map(lambda ze: ze.name, zes))
            self.assertSetEqual(str_from_elaboration, str_from_database)
        print("------- [7] END ZONES ZONE DEPENDENCIES TEST -------")

    def test_08_cname_presence(self):
        """
        Checks data integrity between aliases retrieved from elaboration and aliases relations saved in the DB.

        """
        print("\n------- [8] START ALIASES PRESENCE CHECK -------")
        aliases_rr = set()
        zone_name_cnames_rr = set()
        for zone in self.dns_results.zone_dependencies_per_zone.keys():
            if len(zone.name_path.get_aliases_chain()) == 0:
                pass
            elif len(zone.name_path.get_aliases_chain()) == 1:
                zone_name_cnames_rr.add(zone.name_path.get_aliases_chain()[0])
            else:
                for rr in zone.name_path.get_aliases_chain()[0:-1]:
                    aliases_rr.add(rr)
                zone_name_cnames_rr.add(zone.name_path.get_aliases_chain()[-1])
            for name_server_path in zone.name_servers:
                for rr in name_server_path.get_aliases_chain():
                    aliases_rr.add(rr)
        # actual cname testing
        print(f"{len(aliases_rr)+len(zone_name_cnames_rr)} CNAMEs in total")
        for rr in aliases_rr:
            try:
                alias_dne = helper_alias.get_alias(rr.name)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            str_from_elaboration = rr.get_first_value().string
            str_from_database = alias_dne.name
            self.assertEqual(str_from_elaboration, str_from_database)
        for rr in zone_name_cnames_rr:
            try:
                atza = helper_alias_to_zone.get_from_domain_name(rr.name)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            str_from_elaboration = rr.get_first_value().string
            str_from_database = atza.zone.name
            self.assertEqual(str_from_elaboration, str_from_database)
        print("------- [8] END ALIASES PRESENCE CHECK -------")

    def test_09_getting_direct_zone_of_domain_name(self):
        print("\n------- [9] START ZONE DEPENDENCIES PER ZONE INTEGRITY CHECK -------")
        for domain_name in self.dns_results.direct_zones.keys():
            try:
                ze = helper_zone.get_direct_zone_of(domain_name)
                str_from_database = ze.name
            except DoesNotExist:
                str_from_database = None
            if self.dns_results.direct_zones[domain_name] is None:
                str_from_elaboration = None
            else:
                str_from_elaboration = self.dns_results.direct_zones[domain_name].name.string
            self.assertEqual(str_from_elaboration, str_from_database)
        print("------- [9] END ZONE DEPENDENCIES PER ZONE INTEGRITY CHECK -------")


if __name__ == '__main__':
    unittest.main()
