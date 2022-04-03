import unittest
import selenium
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.SchemeUrl import SchemeUrl
from entities.resolvers.ScriptDependenciesResolver import ScriptDependenciesResolver
from utils import file_utils


class ScriptDependenciesResolvingTestCase(unittest.TestCase):
    results = None
    resolver = None
    headless_browser = None
    urls = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.urls = [
            SchemeUrl('https://consent.youtube.com/ml?continue=https://www.youtube.com/feed/explore?gl%3DIT&gl=IT&hl=it&pc=yt&uxe=23983171&src=1'),
            SchemeUrl('https://www.google.com/doodles')
        ]
        # ELABORATION
        PRD = file_utils.get_project_root_directory()
        cls.headless_browser = FirefoxHeadlessWebDriver(PRD)
        cls.resolver = ScriptDependenciesResolver(cls.headless_browser)
        cls.results = dict()
        for url in cls.urls:
            try:
                cls.results[url] = cls.resolver.search_script_application_dependencies(url)
            except selenium.common.exceptions.WebDriverException as e:
                print(f"!!! {str(e)} !!!")
                exit(-1)

    def test_01_debug_prints(self):
        print(f"\n------- [1] START DEBUG PRINTS TEST -------")
        for i, url in enumerate(self.results.keys()):
            print(f"url[{i+1}/{len(self.results.keys())}]: {url}")
            for j, script in enumerate(self.results[url]):
                print(f"--> script[{j+1}/{len(self.results[url])}] integrity={script.integrity}, src={script.src}")
            if i != len(self.results.keys())-1:
                print()
        print(f"------- [1] END DEBUG PRINTS TEST -------")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
