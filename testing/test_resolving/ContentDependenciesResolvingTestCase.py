import unittest
from pathlib import Path
import selenium
from entities.ContentDependenciesResolver import ContentDependenciesResolver
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError


class ContentDependenciesResolvingTestCase(unittest.TestCase):
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
        url = 'https://www.youtube.com/?gl=IT'
        # ELABORATION
        PRD = ContentDependenciesResolvingTestCase.get_project_root_folder()
        try:
            headless_browser = FirefoxHeadlessWebDriver(PRD)
        except (FileWithExtensionNotFoundError, selenium.common.exceptions.WebDriverException) as e:
            print(f"!!! {str(e)} !!!")
            exit(1)
        content_resolver = ContentDependenciesResolver(headless_browser)
        try:
            result = content_resolver.search_script_application_dependencies(url, ['javascript', 'application/'])
            cls.dependencies = result[0]
            cls.scripts = result[1]
        except selenium.common.exceptions.WebDriverException as exc:
            print(f"!!! {str(exc)} !!!")
        headless_browser.close()

    def test_1_print_results(self):
        if len(self.dependencies) == 0 or self.dependencies is None:
            print(f"Found nothing...")
        for index, dep in enumerate(self.dependencies):
            print(f"dependency[{index+1}]: {str(dep)}")
        for index, script in enumerate(self.scripts):
            print(f"script[{index+1}]: {str(script)}")


if __name__ == '__main__':
    unittest.main()
