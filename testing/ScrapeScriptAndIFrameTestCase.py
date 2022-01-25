import unittest
from pathlib import Path
import selenium
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.resolvers.ScriptDependenciesResolver import ScriptDependenciesResolver
from exceptions.FilenameNotFoundError import FilenameNotFoundError


class ScrapeScriptAndIFrameTestCase(unittest.TestCase):
    headless_browser = None
    browser = None
    PRD = None

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
        url = 'http://127.0.0.1:3000/'
        # url = 'https://corriere.it'
        # ELABORATION
        PRD = ScrapeScriptAndIFrameTestCase.get_project_root_folder()
        try:
            cls.headless_browser = FirefoxHeadlessWebDriver(PRD)
        except (FilenameNotFoundError, selenium.common.exceptions.WebDriverException) as e:
            print(f"!!! {str(e)} !!!")
            return
        script_resolver = ScriptDependenciesResolver(cls.headless_browser)
        try:
            cls.scripts = script_resolver.search_script_application_dependencies(url)
        except selenium.common.exceptions.WebDriverException as exc:
            print(f"!!! type={type(exc)}, str={str(exc)} !!!")

    def test_1_print_debugs(self):
        print(f"\n------- [1] START PRINTING TEST -------")
        for index, script in enumerate(self.scripts):
            print(f"script[{index+1}/{len(self.scripts)}]: {str(script)}")
        print(f"------- [1] END PRINTING TEST -------")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
