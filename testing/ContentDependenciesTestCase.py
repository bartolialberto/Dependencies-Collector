import unittest
from pathlib import Path
import selenium
from entities.ContentDependenciesResolver import ContentDependenciesResolver
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import domain_name_utils


class ContentDependenciesTestCase(unittest.TestCase):
    content_resolver = None
    headless_browser = None

    @classmethod
    def setUpClass(cls) -> None:
        try:
            headless_browser = FirefoxHeadlessWebDriver(Path.cwd().parent)
        except selenium.common.exceptions.WebDriverException as exc1:
            print(f"!!! {str(exc1)} !!!")
            exit(1)
        except FileWithExtensionNotFoundError as exc2:
            print(f"!!! {exc2.message} !!!")
            exit(1)
        cls.content_resolver = ContentDependenciesResolver(headless_browser)

    def setUp(self) -> None:
        # Format
        # landing_page_results = dict with domain name as key
        # value of a key is a tuple of 3 elements: (landing_url as string, redirection path as a list of string, if it is hsts as boolean)
        self.landing_page_results = {
            'google.it': (
                'https://consent.google.it/ml?continue=https://www.google.it/&gl=IT&m=0&pc=shp&hl=it&src=1',
                ['https://google.it/', 'https://www.google.it/', 'https://consent.google.it/ml?continue=https://www.google.it/&gl=IT&m=0&pc=shp&hl=it&src=1'],
                False
            ),
            'youtube.de': (
                'https://www.youtube.com/?gl=DE',
                ['https://youtube.de/', 'https://www.youtube.com/?gl=DE'],
                False
            )
         }

    def test_search_for_script_dependencies(self):
        print(f"test_search_for_script_dependencies ****************************************************************")
        for domain_name in self.landing_page_results.keys():
            print(f"Searching dependencies for domain '{domain_name}'")
            print(f"Deducted url: {domain_name} --> {domain_name_utils.deduct_http_url(domain_name)}")
            try:
                content_dependencies = self.content_resolver.search_script_application_dependencies(self.landing_page_results[domain_name][0], ['javascript', 'application/'])
                for index, dep in enumerate(content_dependencies):
                    print(f"--> [{index + 1}]: {str(dep)}")
                print(f"javascript/application dependencies found: {len(content_dependencies)}.\n")
            except selenium.common.exceptions.WebDriverException as exc:
                print(f"!!! {str(exc)} !!!")

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.content_resolver is not None:
            cls.content_resolver.close()


if __name__ == '__main__':
    unittest.main()
