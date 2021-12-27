import unittest
from pathlib import Path
import selenium
from entities.ContentDependenciesResolver import ContentDependenciesResolver
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from exceptions.ReachedDOMRootError import ReachedDOMRootError


class ScrapeScriptAndIFrameTestCase(unittest.TestCase):
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
        cls.PRD = ScrapeScriptAndIFrameTestCase.get_project_root_folder()
        cls.browser = FirefoxHeadlessWebDriver(cls.PRD)
        cls.resolver = ContentDependenciesResolver(cls.browser)
        # PARAMETER
        cls.url = 'http://127.0.0.1:3000/'

    def test_script_in_iframe(self):
        print(f"DEBUG PRINTS:")
        try:
            scripts = self.resolver.test(self.url)
            for i, script in enumerate(scripts):
                print(f"--> [{i + 1}/{len(scripts)}] = src:{script.get_attribute('src')}", end='')
                try:
                    iframe = self.resolver.try_to_get_iframe_parent(script)
                    print(f" is in iframe")
                except ReachedDOMRootError:
                    print(f"")
                    pass
        except selenium.common.exceptions.WebDriverException:
            raise
        finally:
            self.browser.close()


if __name__ == '__main__':
    unittest.main()
