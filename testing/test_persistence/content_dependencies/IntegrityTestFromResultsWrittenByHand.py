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
    Test class that takes a list the result from a landing page resolver and then executes:

    1- the insertion of the landing pages entities (if necessary)

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
        cls.landing_page_results = {
            # key is domain name
            'youtube.de': (
                # value is tuple: tuple[0] is landing url, tuple[1] is list of redirection path (url), tuple[2] is strict-transport-security-presence
                'https://www.youtube.com/?gl=DE',
                [
                    'https://youtube.de/',
                    'https://www.youtube.com/?gl=DE'
                ],
                False
            ),
            'google.it': (
                'https://consent.google.it/ml?continue=https://www.google.it/&gl=IT&m=0&pc=shp&hl=it&src=1',
                [
                    'https://google.it/',
                    'https://www.google.it/',
                    'https://consent.google.it/ml?continue=https://www.google.it/&gl=IT&m=0&pc=shp&hl=it&src=1'
                ],
                False
            )
         }

    @staticmethod
    def set_up_resolver(project_root_directory: Path):
        try:
            headless_browser = FirefoxHeadlessWebDriver(project_root_directory)
        except FileWithExtensionNotFoundError as e:
            print(f"!!! {e.message} !!!")
            exit(1)
        return ContentDependenciesResolver(headless_browser)

    @staticmethod
    def content_dependencies_resolver(content_resolver: ContentDependenciesResolver, landing_page_results: dict):
        print("\nSTART CONTENT DEPENDENCIES RESOLVER")
        content_dependencies_result = dict()
        for domain_name in landing_page_results.keys():
            print(f"Searching content dependencies for: {landing_page_results[domain_name][0]}")
            try:
                result = content_resolver.search_script_application_dependencies(landing_page_results[domain_name][0], ['javascript', 'application/'])
                content_dependencies = result[0]
                for index, dep in enumerate(content_dependencies):
                    print(f"--> [{index + 1}]: {str(dep)}")
                content_dependencies_result[landing_page_results[domain_name][0]] = content_dependencies
            except selenium.common.exceptions.WebDriverException as exc:
                print(f"!!! {str(exc)} !!!")
        print("END CONTENT DEPENDENCIES RESOLVER")
        return content_dependencies_result

    def setUp(self) -> None:
        self.PRD = IntegrityTestFromElaboration.get_project_root_folder()
        helper_landing_page.multiple_inserts(self.landing_page_results)
        self.content_resolver = IntegrityTestFromElaboration.set_up_resolver(self.PRD)
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
