import unittest
from pathlib import Path
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.DatabaseEntitiesCompleter import DatabaseEntitiesCompleter
from persistence import helper_application_results, helper_domain_name, helper_name_server, helper_zone, \
    helper_web_site, helper_web_server, helper_mail_domain, helper_mail_server, helper_script, helper_script_server
from persistence.BaseModel import db, project_root_directory_name
from utils import domain_name_utils


class EntireApplicationIntegrityTestCase(unittest.TestCase):
    input_mail_domains = None
    input_websites = None
    headless_browser_is_instantiated = None
    resolvers = None

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
        cls.input_websites = ['google.it/doodles', 'www.youtube.it/feed/explore']
        cls.input_mail_domains = ['gmail.com', 'outlook.com']
        complete_unresolved_database = True
        consider_tld = False
        execute_rov_scraping = False
        # SET UP
        PRD = EntireApplicationIntegrityTestCase.get_project_root_folder()
        cls.resolvers = ApplicationResolversWrapper(consider_tld, execute_rov_scraping, project_root_directory=PRD)
        cls.headless_browser_is_instantiated = True
        if complete_unresolved_database:
            print("********** START COMPLETING PREVIOUS APPLICATION ELABORATION **********")
            completer = DatabaseEntitiesCompleter(cls.resolvers)
            unresolved_entities = helper_application_results.get_unresolved_entities()
            completer.do_complete_unresolved_entities(unresolved_entities)
        print("********** START ACTUAL APPLICATION ELABORATION **********")
        preamble_domain_names = cls.resolvers.do_preamble_execution(cls.input_websites, cls.input_mail_domains)
        midst_domain_names = cls.resolvers.do_midst_execution(preamble_domain_names)
        cls.resolvers.do_epilogue_execution(midst_domain_names)
        print("\nInsertion into database started... ")
        helper_application_results.insert_all_application_results(cls.resolvers)
        print("Insertion into database finished.")

    # ----- WATCHOUT FOR TRANSIENT ERRORS. TEST FAILS DEPENDS UPON THEM. -----

    def test_01_domain_names_presence(self):
        print("\n------- [1] START EVERY DOMAIN NAME PRESENCE TEST -------")
        tmp = helper_domain_name.get_everyone()
        db_domain_names = set(map(lambda dne: dne.string, tmp))
        elaboration_domain_names = set(self.resolvers.total_dns_results.zone_dependencies_per_domain_name.keys())
        for web_site in self.resolvers.landing_web_sites_results.keys():
            web_site_domain_name = domain_name_utils.deduct_domain_name(web_site)
            web_site_domain_name = domain_name_utils.insert_trailing_point(web_site_domain_name)
            elaboration_domain_names.add(web_site_domain_name)
            landing_res = self.resolvers.landing_web_sites_results[web_site]
            if landing_res.https is not None:
                for dn in landing_res.https.access_path:
                    elaboration_domain_names.add(dn)
            if landing_res.http is not None:
                for dn in landing_res.http.access_path:
                    elaboration_domain_names.add(dn)
        for script_site in self.resolvers.landing_script_sites_results.keys():
            script_site_domain_name = domain_name_utils.deduct_domain_name(script_site)
            script_site_domain_name = domain_name_utils.insert_trailing_point(script_site_domain_name)
            elaboration_domain_names.add(script_site_domain_name)
            landing_res = self.resolvers.landing_script_sites_results[script_site]
            if landing_res.https is not None:
                for dn in landing_res.https.access_path:
                    elaboration_domain_names.add(dn)
            if landing_res.http is not None:
                for dn in landing_res.http.access_path:
                    elaboration_domain_names.add(dn)
        for mail_domain in self.input_mail_domains:
            md = domain_name_utils.insert_trailing_point(mail_domain)
            elaboration_domain_names.add(md)
        for mail_domain in self.resolvers.mail_domains_results.dependencies.keys():
            for mail_server in self.resolvers.mail_domains_results.dependencies[mail_domain].mail_servers:
                elaboration_domain_names.add(mail_server)
        for name_server in self.resolvers.total_dns_results.zone_name_dependencies_per_name_server.keys():
            elaboration_domain_names.add(name_server)
        self.assertSetEqual(elaboration_domain_names, db_domain_names)
        print(f"Reached this print means everything went well")
        print("------- [1] END EVERY DOMAIN NAME PRESENCE TEST -------")

    def test_02_name_servers_presence(self):
        print("\n------- [2] START EVERY NAME SERVER PRESENCE TEST -------")
        tmp = helper_name_server.get_everyone()
        db_name_servers = set(map(lambda nse: nse.name.string, tmp))
        elaboration_name_servers = set(self.resolvers.total_dns_results.zone_name_dependencies_per_name_server.keys())
        self.assertSetEqual(elaboration_name_servers, db_name_servers)
        print(f"Reached this print means everything went well")
        print("------- [2] END EVERY NAME SERVER PRESENCE TEST -------")

    def test_03_zones_presence(self):
        print("\n------- [3] START EVERY ZONE PRESENCE TEST -------")
        tmp = helper_zone.get_everyone()
        db_zones = set(map(lambda ze: ze.name, tmp))
        elaboration_zones = set(self.resolvers.total_dns_results.zone_name_dependencies_per_zone.keys())
        self.assertSetEqual(elaboration_zones, db_zones)
        print(f"Reached this print means everything went well")
        print("------- [3] END EVERY ZONE PRESENCE TEST -------")

    def test_04_zone_dependencies_per_domain_name_integrity(self):
        print("\n------- [4] START EVERY DOMAIN NAME ZONE DEPENDENCIES INTEGRITY TEST -------")
        for domain_name in self.resolvers.total_dns_results.zone_dependencies_per_domain_name.keys():
            tmp = helper_zone.get_zone_dependencies_of_string_domain_name(domain_name)
            db_zone_names = set(map(lambda ze: ze.name, tmp))
            elaboration_zone_names = set(map(lambda zo: zo.name, self.resolvers.total_dns_results.zone_dependencies_per_domain_name[domain_name]))
            self.assertSetEqual(elaboration_zone_names, db_zone_names)
        print(f"Reached this print means everything went well")
        print("------- [4] END EVERY DOMAIN NAME ZONE DEPENDENCIES INTEGRITY TEST -------")

    def test_05_zone_dependencies_per_name_server_integrity(self):
        print("\n------- [5] START EVERY NAME SERVER ZONE DEPENDENCIES INTEGRITY TEST -------")
        for name_server in self.resolvers.total_dns_results.zone_name_dependencies_per_name_server.keys():
            tmp = helper_zone.get_zone_dependencies_of_string_domain_name(name_server)
            db_zone_names = set(map(lambda ze: ze.name, tmp))
            elaboration_zone_names = set(self.resolvers.total_dns_results.zone_name_dependencies_per_name_server[name_server])
            self.assertSetEqual(elaboration_zone_names, db_zone_names)
        print(f"Reached this print means everything went well")
        print("------- [5] END EVERY NAME SERVER ZONE DEPENDENCIES INTEGRITY TEST -------")

    def test_06_zone_dependencies_per_zone_name_integrity(self):
        print("\n------- [6] START EVERY ZONE NAME ZONE DEPENDENCIES INTEGRITY TEST -------")
        for zone_name in self.resolvers.total_dns_results.zone_name_dependencies_per_zone.keys():
            tmp = helper_zone.get_zone_dependencies_of_zone_name(zone_name)
            db_zone_names = set(map(lambda ze: ze.name, tmp))
            elaboration_zone_names = set(self.resolvers.total_dns_results.zone_name_dependencies_per_zone[zone_name])
            self.assertSetEqual(elaboration_zone_names, db_zone_names)
        print(f"Reached this print means everything went well")
        print("------- [6] END EVERY ZONE NAME ZONE DEPENDENCIES INTEGRITY TEST -------")

    def test_07_zone_dependencies_per_zone_name_integrity(self):
        print("\n------- [7] START EVERY DOMAIN NAME DIRECT ZONE INTEGRITY TEST -------")
        for domain_name in self.resolvers.total_dns_results.direct_zone_name_per_domain_name.keys():
            tmp = helper_zone.get_direct_zone_object_of(domain_name)
            db_zone_name = tmp.name
            elaboration_zone_name = self.resolvers.total_dns_results.direct_zone_name_per_domain_name[domain_name]
            self.assertEqual(elaboration_zone_name, db_zone_name)
        print(f"Reached this print means everything went well")
        print("------- [7] END EVERY DOMAIN NAME DIRECT ZONE INTEGRITY TEST -------")

    def test_08_mail_domains_presence(self):
        print("\n------- [8] START EVERY MAIL DOMAIN PRESENCE TEST -------")
        tmp = helper_mail_domain.get_everyone()
        db_mail_domains = set(map(lambda mde: mde.name.string, tmp))
        elaboration_mail_domains = set(map(lambda md: domain_name_utils.insert_trailing_point(md), self.input_mail_domains))
        self.assertEqual(elaboration_mail_domains, db_mail_domains)
        print(f"Reached this print means everything went well")
        print("------- [8] END EVERY MAIL DOMAIN PRESENCE TEST -------")

    def test_09_mail_servers_dependencies(self):
        print("\n------- [9] START MAIL SERVER DEPENDENCIES INTEGRITY TEST -------")
        for mail_domain in self.resolvers.mail_domains_results.dependencies.keys():
            tmp = helper_mail_server.get_every_of(mail_domain)
            db_mail_servers = set(map(lambda mse: mse.name.string, tmp))
            elaboration_mail_servers = set(self.resolvers.mail_domains_results.dependencies[mail_domain].mail_servers)
            self.assertEqual(elaboration_mail_servers, db_mail_servers)
        print(f"Reached this print means everything went well")
        print("------- [9] END EVERY MAIL DEPENDENCIES INTEGRITY TEST -------")

    def test_10_web_site_script_dependencies_integrity(self):
        print("\n------- [10] START MAIL SERVER DEPENDENCIES INTEGRITY TEST -------")
        for web_site in self.resolvers.web_site_script_dependencies.keys():
            # HTTPS
            tmp = helper_script.get_from_with_scheme(web_site, True)
            if len(tmp) == 0:
                db_https_scripts = set()
            else:
                temp = set(filter(lambda s: s is not None, tmp))
                db_https_scripts = set(map(lambda s: s.src, temp))
            if self.resolvers.web_site_script_dependencies[web_site].https is None:
                elaboration_https_scripts = set()
            else:
                elaboration_https_scripts = set(map(lambda mps: mps.src, self.resolvers.web_site_script_dependencies[web_site].https))
            # HTTP
            tmp = helper_script.get_from_with_scheme(web_site, False)
            if len(tmp) == 0:
                db_http_scripts = set()
            else:
                temp = set(filter(lambda s: s is not None, tmp))
                db_http_scripts = set(map(lambda s: s.src, temp))
            if self.resolvers.web_site_script_dependencies[web_site].http is None:
                elaboration_http_scripts = set()
            else:
                elaboration_http_scripts = set(map(lambda mps: mps.src, self.resolvers.web_site_script_dependencies[web_site].http))
            self.assertEqual(elaboration_http_scripts, db_http_scripts)
            self.assertEqual(elaboration_https_scripts, db_https_scripts)
        print(f"Reached this print means everything went well")
        print("------- [10] END EVERY MAIL DEPENDENCIES INTEGRITY TEST -------")

    def test_11_web_sites_presence(self):
        print("\n------- [11] START EVERY WEB SITE PRESENCE TEST -------")
        tmp = helper_web_site.get_everyone()
        db_web_sites = set(map(lambda wse: wse.url.string, tmp))
        elaboration_web_sites = set(self.input_websites)
        self.assertSetEqual(elaboration_web_sites, db_web_sites)
        print(f"Reached this print means everything went well")
        print("------- [x] END EVERY WEB SITE PRESENCE TEST -------")

    def test_12_web_servers_presence(self):
        print("\n------- [12] START EVERY WEB SERVERS PRESENCE TEST -------")
        tmp = helper_web_server.get_everyone()
        db_web_servers = set(map(lambda wse: wse.name.string, tmp))
        elaboration_web_servers = set()
        for web_site in self.resolvers.landing_web_sites_results.keys():
            landing_res = self.resolvers.landing_web_sites_results[web_site]
            if landing_res.https is not None:
                elaboration_web_servers.add(landing_res.https.server)
            if landing_res.http is not None:
                elaboration_web_servers.add(landing_res.http.server)
        self.assertSetEqual(elaboration_web_servers, db_web_servers)
        print(f"Reached this print means everything went well")
        print("------- [12] END EVERY WEB SERVERS PRESENCE TEST -------")

    def test_13_web_sites_landing_integrity(self):
        print("\n------- [13] START WEB SITE LANDING INTEGRITY TEST -------")
        for web_site in self.resolvers.landing_web_sites_results.keys():
            # HTTPS
            wse = helper_web_server.get_from(web_site, True, first_only=True)
            if wse is None:
                db_web_server_https = None
            else:
                db_web_server_https = wse.name.string
            if self.resolvers.landing_web_sites_results[web_site].https is None:
                elaboration_web_server_https = None
            else:
                elaboration_web_server_https = self.resolvers.landing_web_sites_results[web_site].https.server
            # HTTP
            wse = helper_web_server.get_from(web_site, False, first_only=True)
            if wse is None:
                db_web_server_http = None
            else:
                db_web_server_http = wse.name.string
            if self.resolvers.landing_web_sites_results[web_site].http is None:
                elaboration_web_server_http = None
            else:
                elaboration_web_server_http = self.resolvers.landing_web_sites_results[web_site].http.server
            self.assertEqual(elaboration_web_server_http, db_web_server_http)
            self.assertEqual(elaboration_web_server_https, db_web_server_https)
        print(f"Reached this print means everything went well")
        print("------- [13] END WEB SITE LANDING INTEGRITY TEST -------")

    def test_14_script_sites_landing_integrity(self):
        print("\n------- [14] START SCRIPT SITE LANDING INTEGRITY TEST -------")
        for script_site in self.resolvers.landing_script_sites_results.keys():
            # HTTPS
            sse = helper_script_server.get_from_string_script_site(script_site, True, first_only=True)
            if sse is None:
                db_script_server_https = None
            else:
                db_script_server_https = sse.name.string
            if self.resolvers.landing_script_sites_results[script_site].https is None:
                elaboration_script_server_https = None
            else:
                elaboration_script_server_https = self.resolvers.landing_script_sites_results[script_site].https.server
            # HTTP
            sse = helper_script_server.get_from_string_script_site(script_site, False, first_only=True)
            if sse is None:
                db_script_server_http = None
            else:
                db_script_server_http = sse.name.string
            if self.resolvers.landing_script_sites_results[script_site].http is None:
                elaboration_script_server_http = None
            else:
                elaboration_script_server_http = self.resolvers.landing_script_sites_results[script_site].http.server
            self.assertEqual(elaboration_script_server_http, db_script_server_http)
            self.assertEqual(elaboration_script_server_https, db_script_server_https)
        print(f"Reached this print means everything went well")
        print("------- [14] END SCRIPT SITE LANDING INTEGRITY TEST -------")

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.headless_browser_is_instantiated:
            cls.resolvers.headless_browser.close()
        db.close()


if __name__ == '__main__':
    unittest.main()
