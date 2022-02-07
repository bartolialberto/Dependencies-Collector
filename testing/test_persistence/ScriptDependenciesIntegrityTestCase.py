import unittest
from typing import Tuple, Dict, Set
import selenium
from peewee import DoesNotExist
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.resolvers.DnsResolver import DnsResolver
from entities.resolvers.LandingResolver import LandingResolver
from entities.resolvers.ScriptDependenciesResolver import ScriptDependenciesResolver, MainPageScript
from entities.resolvers.results.ScriptDependenciesResult import ScriptDependenciesResult
from exceptions.InvalidUrlError import InvalidUrlError
from persistence import helper_script, helper_application_results, helper_web_site
from utils import url_utils, file_utils


class ScriptDependenciesIntegrityTestCase(unittest.TestCase):
    web_site_landing_results = None
    web_site_script_dependencies = None
    script_script_site_dependencies = None
    resolver = None
    headless_browser = None
    web_sites = None

    @staticmethod
    def do_script_dependencies_resolving(script_resolver, landing_web_sites_results) -> Dict[str, ScriptDependenciesResult]:
        print("\n\nSTART SCRIPT DEPENDENCIES RESOLVER")
        script_dependencies_result = dict()
        for website in landing_web_sites_results.keys():
            print(f"Searching script dependencies for website: {website}")
            https_result = landing_web_sites_results[website].https
            http_result = landing_web_sites_results[website].http

            if https_result is None and http_result is None:
                print(f"!!! Neither HTTPS nor HTTP landing possible for: {website} !!!")
                script_dependencies_result[website] = ScriptDependenciesResult(None, None)
            elif https_result is None and http_result is not None:
                # HTTPS
                print(f"******* via HTTPS *******")
                print(f"--> No landing possible")
                # HTTP
                print(f"******* via HTTP *******")
                http_landing_page = http_result.url
                try:
                    http_scripts = script_resolver.search_script_application_dependencies(http_landing_page)
                    for i, script in enumerate(http_scripts):
                        print(f"script[{i+1}/{len(http_scripts)}]: integrity={script.integrity}, src={script.src}")
                    script_dependencies_result[website] = ScriptDependenciesResult(None, http_scripts)
                except selenium.common.exceptions.WebDriverException as e:
                    print(f"!!! {str(e)} !!!")
                    http_scripts = None
            elif http_result is None and https_result is not None:
                # HTTP
                print(f"******* via HTTP *******")
                print(f"--> No landing possible")
                # HTTPS
                print(f"******* via HTTPS *******")
                https_landing_page = https_result.url
                try:
                    https_scripts = script_resolver.search_script_application_dependencies(https_landing_page)
                    for i, script in enumerate(https_scripts):
                        print(f"script[{i+1}/{len(https_scripts)}]: integrity={script.integrity}, src={script.src}")
                    script_dependencies_result[website] = ScriptDependenciesResult(https_scripts, None)
                except selenium.common.exceptions.WebDriverException as e:
                    print(f"!!! {str(e)} !!!")
                    https_scripts = None
            else:
                # HTTPS
                print(f"******* via HTTPS *******")
                https_landing_page = https_result.url
                try:
                    https_scripts = script_resolver.search_script_application_dependencies(https_landing_page)
                    for i, script in enumerate(https_scripts):
                        print(f"script[{i+1}/{len(https_scripts)}]: integrity={script.integrity}, src={script.src}")
                except selenium.common.exceptions.WebDriverException as e:
                    print(f"!!! {str(e)} !!!")
                    https_scripts = None

                # HTTP
                print(f"******* via HTTP *******")
                http_landing_page = http_result.url
                try:
                    http_scripts = script_resolver.search_script_application_dependencies(http_landing_page)
                    for i, script in enumerate(https_scripts):
                        print(f"script[{i+1}/{len(https_scripts)}]: integrity={script.integrity}, src={script.src}")
                except selenium.common.exceptions.WebDriverException as e:
                    print(f"!!! {str(e)} !!!")
                    http_scripts = None
                script_dependencies_result[website] = ScriptDependenciesResult(https_scripts, http_scripts)
            print('')
        print("END SCRIPT DEPENDENCIES RESOLVER")
        return script_dependencies_result

    @staticmethod
    def extract_script_hosting_dependencies(web_site_script_dependencies) -> Tuple[Dict[MainPageScript, Set[str]], Set[str]]:
        result = dict()
        script_sites = set()
        for web_site in web_site_script_dependencies.keys():
            https_scripts = web_site_script_dependencies[web_site].https
            http_scripts = web_site_script_dependencies[web_site].http
            if https_scripts is None:
                pass
            else:
                for script in https_scripts:
                    try:
                        script_site = url_utils.deduct_second_component(script.src)
                    except InvalidUrlError:
                        continue
                    script_sites.add(script_site)
                    try:
                        result[script]
                    except KeyError:
                        result[script] = set()
                    finally:
                        result[script].add(script_site)
            if http_scripts is None:
                pass
            else:
                for script in http_scripts:
                    try:
                        script_site = url_utils.deduct_second_component(script.src)
                    except InvalidUrlError:
                        continue
                    script_sites.add(script_site)
                    try:
                        result[script]
                    except KeyError:
                        result[script] = set()
                    finally:
                        result[script].add(script_site)
        return result, script_sites

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.web_sites = {
            'www.google.com/doodles',
            'www.youtube.com/feed/explore'
        }
        # ELABORATION
        PRD = file_utils.get_project_root_directory()
        cls.headless_browser = FirefoxHeadlessWebDriver(PRD)
        script_resolver = ScriptDependenciesResolver(cls.headless_browser)
        dns_resolver = DnsResolver(None)
        landing_resolver = LandingResolver(dns_resolver)
        # ELABORATION: resolving
        cls.web_site_landing_results = landing_resolver.resolve_sites(cls.web_sites)
        cls.web_site_script_dependencies = ScriptDependenciesIntegrityTestCase.do_script_dependencies_resolving(script_resolver, cls.web_site_landing_results)
        cls.script_script_site_dependencies, cls.script_sites = ScriptDependenciesIntegrityTestCase.extract_script_hosting_dependencies(cls.web_site_script_dependencies)
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
            # HTTPS
            https = True
            if self.web_site_script_dependencies[web_site].https is None:
                https_script_src_elaboration = set()
            else:
                https_script_src_elaboration = set(
                    map(lambda s: s.src, self.web_site_script_dependencies[web_site].https))
            try:
                https_ses = helper_script.get_from_with_scheme(web_site, https)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            https_script_src_database = set(map(lambda se: se.src, https_ses))
            # HTTP
            https = False
            if self.web_site_script_dependencies[web_site].http is None:
                http_script_src_elaboration = set()
            else:
                http_script_src_elaboration = set(map(lambda s: s.src, self.web_site_script_dependencies[web_site].http))
            try:
                http_ses = helper_script.get_from_with_scheme(web_site, https)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            http_script_src_database = set(map(lambda se: se.src, http_ses))
            print(f"--- web site = {web_site} ----------")
            print(f"from HTTPS elaboration {len(https_script_src_elaboration)} scripts, from HTTP elaboration {len(http_script_src_elaboration)} scripts")
            print(f"from HTTPS database {len(https_script_src_database)} scripts, from HTTP database {len(http_script_src_database)} scripts")
            self.assertSetEqual(https_script_src_elaboration, https_script_src_database)
            self.assertSetEqual(http_script_src_elaboration, http_script_src_database)
        print(f"\nIf this print is reached, then everything went fine...")
        print(f"------- [2] END DATA INTEGRITY OF SCRIPT DEPENDENCIES PER WEB SITE TEST -------")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
