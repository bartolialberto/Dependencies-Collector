import unittest
from pathlib import Path
from typing import List
import requests
import selenium
from peewee import DoesNotExist
from entities.ContentDependenciesResolver import ContentDependenciesResolver
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from persistence import helper_content_dependency, helper_landing_page
from persistence.BaseModel import db
from utils import requests_utils


class IntegrityTestFromElaboration(unittest.TestCase):
    """
    Test class that takes a list of domain names and then executes:

    1- the landing page resolving (with optional DB insertion if needed)

    2- the content dependencies resolving

    3- insertion of the dependencies' result in the DB

    Finally checks the integrity of the dependencies found with what was saved and retrieved from the database.

    """
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
        cls.domain_name_list = ['google.it', 'unipd.it', 'youtube.it']

    @staticmethod
    def set_up_resolver(project_root_folder: Path):
        try:
            headless_browser = FirefoxHeadlessWebDriver(project_root_folder)
        except FileWithExtensionNotFoundError as e:
            print(f"!!! {e.message} !!!")
            exit(1)
        return ContentDependenciesResolver(headless_browser)

    @staticmethod
    def landing_page_resolving(domain_name_list: List[str]):
        print("START LANDING PAGE RESOLVER")
        landing_page_results = dict()
        for domain_name in domain_name_list:
            print(f"\nTrying to connect to domain '{domain_name}' via HTTPS:")
            try:
                (landing_url, redirection_path, hsts) = requests_utils.resolve_landing_page(domain_name)
                print(f"Landing url: {landing_url}")
                print(f"HTTP Strict Transport Security: {hsts}")
                print(f"Redirection path:")
                for index, url in enumerate(redirection_path):
                    print(f"[{index + 1}/{len(redirection_path)}]: {url}")
                landing_page_results[domain_name] = (landing_url, redirection_path, hsts)
            except requests.exceptions.ConnectionError as exc:  # exception that contains the case in which HTTPS is not supported by the server
                try:
                    # TODO: caso in cui c'è una ConnectionError ma non è il caso in cui è supportato solo http... Come si fa?
                    (landing_url, redirection_path, hsts) = requests_utils.resolve_landing_page(domain_name, as_https=False)
                    print(f"It seems that HTTPS is not supported by server. Trying with HTTP:")
                    print(f"Landing url: {landing_url}")
                    print(f"HTTP Strict Transport Security: {hsts}")
                    print(f"Redirection path:")
                    for index, url in enumerate(redirection_path):
                        print(f"[{index + 1}/{len(redirection_path)}]: {url}")
                    landing_page_results[domain_name] = (landing_url, redirection_path, hsts)
                except Exception as exc:  # sono tante!
                    print(f"!!! {str(exc)} !!!")
            except Exception as exc:  # sono tante!
                print(f"!!! {str(exc)} !!!")
        print("END LANDING PAGE RESOLVER")
        return landing_page_results

    @staticmethod
    def content_dependencies_resolver(content_resolver: ContentDependenciesResolver, landing_page_results: dict):
        print("\nSTART CONTENT DEPENDENCIES RESOLVER")
        content_dependencies_result = dict()
        for domain_name in landing_page_results.keys():
            print(f"Searching content dependencies for: {landing_page_results[domain_name][0]}")
            try:
                content_dependencies = content_resolver.search_script_application_dependencies(
                    landing_page_results[domain_name][0], ['javascript', 'application/'])
                for index, dep in enumerate(content_dependencies):
                    print(f"--> [{index + 1}]: {str(dep)}")
                content_dependencies_result[landing_page_results[domain_name][0]] = content_dependencies
            except selenium.common.exceptions.WebDriverException as exc:
                print(f"!!! {str(exc)} !!!")
        print("END CONTENT DEPENDENCIES RESOLVER")
        return content_dependencies_result

    def setUp(self) -> None:
        self.PRD = IntegrityTestFromElaboration.get_project_root_folder()
        self.content_resolver = IntegrityTestFromElaboration.set_up_resolver(self.PRD)
        self.landing_page_results = IntegrityTestFromElaboration.landing_page_resolving(self.domain_name_list)
        helper_landing_page.multiple_inserts(self.landing_page_results)
        self.results = IntegrityTestFromElaboration.content_dependencies_resolver(self.content_resolver, self.landing_page_results)
        try:
            helper_content_dependency.multiple_inserts(self.results)
        except DoesNotExist:
            print(f"!!! ERROR: some entities don't exist. !!!")
            exit(1)

    def test_integrity(self):
        print("\nSTART INTEGRITY CHECK")
        for key in self.landing_page_results.keys():
            landing_url = self.landing_page_results[key][0]
            try:
                list_dependencies = helper_content_dependency.get_from_landing_page(landing_url)
            except DoesNotExist:
                print(f"!!! DoesNotExist for LandingPageEntity from url: {landing_url} !!!")
                exit(1)
            self.assertEqual(len(self.results[landing_url]), len(list_dependencies))
            print(f"Tot dependencies for {landing_url}:")
            print(f"--> number of dependencies found from elaboration: {len(self.results[landing_url])}")
            print(f"--> number of dependencies found in the database: {len(list_dependencies)}")
            # integrity test
            for dep in self.results[landing_url]:
                try:
                    list_dependencies.remove(dep)   # needs an overwritten __eq__ method in ContentDependencyEntry class
                except ValueError:
                    print(f"!!! There's a dependency from elaboration not present in the database: {str(dep)} !!!")
            print(f"DEBUG: len(list_dependencies) = {len(list_dependencies)}")
            # for every dependency of the elaboration, it is removed from the list (of dependencies) retrieved from the
            # database. So in the end, if everything is correct, the list should be empty.
            self.assertEqual(0, len(list_dependencies))
            print("")
        self.content_resolver.headless_browser.close()
        db.close()
        print("END INTEGRITY CHECK")


if __name__ == '__main__':
    unittest.main()
