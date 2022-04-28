import unittest
from peewee import DoesNotExist
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.DomainName import DomainName
from persistence import helper_application_results, helper_mail_domain, helper_mail_server
from utils import file_utils


class MailDomainResolvingIntegrityCase(unittest.TestCase):
    results = None
    domain_names = None
    resolvers = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_names = [
            DomainName('acus.gov.')
        ]
        consider_tld = False
        # ELABORATION
        execute_script_resolving = False
        execute_rov_scraping = False
        take_snapshot = False
        PRD = file_utils.get_project_root_directory()
        cls.resolvers = ApplicationResolversWrapper(consider_tld, execute_script_resolving, execute_rov_scraping, PRD, take_snapshot)
        cls.results = cls.resolvers.do_mail_servers_resolving(cls.domain_names)
        print(f"\nInsertion into database... ", end='')
        helper_application_results.insert_mail_servers_resolving(cls.results)
        print(f"DONE.")

    def test_01_mail_domains_presence(self):
        print("\n------- START TEST 1 -------")
        for mail_domain in self.results.dependencies.keys():
            try:
                mde = helper_mail_domain.get(mail_domain)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            self.assertEqual(mail_domain.string, mde.name.string)
        print("------- END TEST 1 -------")

    def test_02_mail_servers_presence(self):
        print("\n------- START TEST 2 -------")
        for mail_domain in self.results.dependencies.keys():
            for mail_server in self.results.dependencies[mail_domain].mail_servers_paths.keys():
                try:
                    mse = helper_mail_server.get(mail_server)
                except DoesNotExist as e:
                    self.fail(f"!!! {str(e)} !!!")
                self.assertEqual(mail_server.string, mse.name.string)
        print("------- END TEST 2 -------")

    def test_03_mail_domain_composed(self):
        print("\n------- START TEST 3 -------")
        for mail_domain in self.results.dependencies.keys():
            try:
                mde = helper_mail_domain.get(mail_domain)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            try:
                mses = helper_mail_server.get_every_of(mde)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            db_str_set = set(map(lambda mse: mse.name.string, mses))
            elaboration_str_set = set(map(lambda ms: ms.string, self.results.dependencies[mail_domain].mail_servers_paths.keys()))
            self.assertSetEqual(elaboration_str_set, db_str_set)
        print("------- END TEST 3 -------")

    def test_04_reversed_mail_domain_composed(self):
        print("\n------- START TEST 4 -------")
        for mail_domain in self.results.dependencies.keys():

            for mail_server in self.results.dependencies[mail_domain].mail_servers_paths.keys():
                try:
                    mse = helper_mail_server.get(mail_server)
                except DoesNotExist as e:
                    self.fail(f"!!! {str(e)} !!!")
                try:
                    mdes = helper_mail_domain.get_every_of(mse)
                except DoesNotExist as e:
                    self.fail(f"!!! {str(e)} !!!")
                db_mde_str_set = set(map(lambda mde: mde.name.string, mdes))
                self.assertIn(mail_domain.string, db_mde_str_set)
        print("------- END TEST 4 -------")


if __name__ == '__main__':
    unittest.main()
