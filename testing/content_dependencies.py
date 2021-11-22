import unittest
from pathlib import Path
import selenium
from entities.ContentDependenciesResolver import ContentDependenciesResolver
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from exceptions.GeckoDriverExecutableNotFoundError import GeckoDriverExecutableNotFoundError


class ContentDependenciesCase(unittest.TestCase):
    def setUp(self) -> None:
        self.domain_name_list = ['google.it']
        self.landing_page_results = {
            'google.it': (
                ['https://google.it/', 'https://www.google.it/', 'https://consent.google.it/ml?continue=https://www.google.it/&gl=IT&m=0&pc=shp&hl=it&src=1'],
                ['google.it', 'google.it', 'consent.google.it']
            )
         }

    def test_search(self):
        headless_browser = FirefoxHeadlessWebDriver(Path.cwd().parent)
        content_resolver = None
        try:
            content_resolver = ContentDependenciesResolver(headless_browser)
        except selenium.common.exceptions.WebDriverException as exc1:
            print(f"!!! {str(exc1)} !!!")
        except GeckoDriverExecutableNotFoundError as exc2:
            print(f"!!! {exc2.message} !!!")
        for domain_name in self.domain_name_list:
            try:
                content_dependencies, content_domain_list = content_resolver.search_script_application_dependencies(self.landing_page_results[domain_name][0][-1])
                for index, dep in enumerate(content_dependencies):
                    print(f"--> [{index + 1}]: {str(dep)}")
                print(f"javascript/application dependencies found: {len(content_dependencies)} on {len(content_domain_list)} domains.")
            except selenium.common.exceptions.WebDriverException as exc:
                print(f"!!! {str(exc)} !!!")
        headless_browser.close()


if __name__ == '__main__':
    unittest.main()
