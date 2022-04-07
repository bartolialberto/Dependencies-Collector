import unittest
from peewee import DoesNotExist
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.Url import Url
from persistence import helper_script, helper_application_results, helper_web_site
from utils import file_utils


class ScriptDependenciesIntegrityTestCase(unittest.TestCase):
    script_script_site_dependencies = None
    web_site_script_dependencies = None
    resolvers = None
    web_sites = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.web_sites = {
            Url('www.google.com/doodles'),
            Url('www.youtube.com/feed/explore')
        }
        # ELABORATION
        PRD = file_utils.get_project_root_directory()
        cls.resolvers = ApplicationResolversWrapper(True, True, False, PRD, False)
        web_site_landing_results = cls.resolvers.do_web_site_landing_resolving(cls.web_sites)
        cls.resolvers.landing_web_sites_results = web_site_landing_results
        cls.resolvers.web_site_script_dependencies = cls.resolvers.do_script_dependencies_resolving()
        cls.script_script_site_dependencies, script_sites = cls.resolvers.extract_script_hosting_dependencies()
        cls.landing_script_sites_results = cls.resolvers.do_script_site_landing_resolving(script_sites)
        cls.web_site_script_dependencies = cls.resolvers.web_site_script_dependencies
        # INSERTION INTO DATABASE
        print("Insertion into database... ", end="")
        for web_site in cls.web_sites:
            helper_web_site.insert(web_site)
        helper_application_results.insert_script_dependencies_resolving(cls.web_site_script_dependencies, cls.script_script_site_dependencies)
        print("DONE")

    def test_1_debug_prints(self):
        print(f"\n------- [1] START DEBUG PRINTS TEST -------")
        for i, web_site in enumerate(self.web_site_script_dependencies.keys()):
            print(f"web site[{i+1}/{len(self.web_site_script_dependencies.keys())}]: {web_site}")
            print(f"***** HTTPS *****")
            if self.web_site_script_dependencies[web_site].https is None:
                print(f"--> No landing so no scripts...")
            else:
                for j, script in enumerate(self.web_site_script_dependencies[web_site].https):
                    print(f"--> script[{j+1}/{len(self.web_site_script_dependencies[web_site].https)}].src={script.src}")
            print(f"***** HTTP *****")
            if self.web_site_script_dependencies[web_site].http is None:
                print(f"--> No landing so no scripts...")
            else:
                for j, script in enumerate(self.web_site_script_dependencies[web_site].http):
                    print(f"--> script[{j+1}/{len(self.web_site_script_dependencies[web_site].http)}].src={script.src}")
            if i != len(self.web_site_script_dependencies.keys())-1:
                print()
        print(f"------- [1] END DEBUG PRINTS TEST -------")

    def test_2_integrity_of_script_dependencies_per_web_site(self):
        print(f"\n------- [2] START DATA INTEGRITY OF SCRIPT DEPENDENCIES PER WEB SITE TEST -------")
        for web_site in self.web_site_script_dependencies.keys():
            try:
                wse = helper_web_site.get(web_site)
            except DoesNotExist:
                raise

            # HTTPS
            https = True
            if self.web_site_script_dependencies[web_site].https is None:
                https_script_src_elaboration = {None}
            else:
                https_script_src_elaboration = set(
                    map(lambda s: s.src, self.web_site_script_dependencies[web_site].https))
            try:
                https_ses = helper_script.get_from_web_site_and_scheme(wse, https)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            https_script_src_database = set()
            if len(https_ses) == 1:
                for se in https_ses:
                    if se is None:
                        https_script_src_database = set()
                    else:
                        https_script_src_database.add(se)
            else:
                https_script_src_database = set(map(lambda se: se.src, https_ses))


            # HTTP
            https = False
            if self.web_site_script_dependencies[web_site].http is None:
                http_script_src_elaboration = {None}
            else:
                http_script_src_elaboration = set(map(lambda s: s.src, self.web_site_script_dependencies[web_site].http))
            try:
                http_ses = helper_script.get_from_web_site_and_scheme(wse, https)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            http_script_src_database = set()
            if len(http_ses) == 1:
                for se in http_ses:
                    if se is None:
                        http_script_src_database = set()
                    else:
                        http_script_src_database.add(se)
            else:
                http_script_src_database = set(map(lambda se: se.src, http_ses))
            print(f"--- web site = {web_site} ----------")
            print(f"from HTTPS elaboration {len(https_script_src_elaboration)} scripts, from HTTP elaboration {len(http_script_src_elaboration)} scripts")
            print(f"from HTTPS database {len(https_script_src_database)} scripts, from HTTP database {len(http_script_src_database)} scripts")
            self.assertSetEqual(https_script_src_elaboration, https_script_src_database)
            self.assertSetEqual(http_script_src_elaboration, http_script_src_database)
        print(f"------- [2] END DATA INTEGRITY OF SCRIPT DEPENDENCIES PER WEB SITE TEST -------")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.resolvers.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
