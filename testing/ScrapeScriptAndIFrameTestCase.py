import unittest
from typing import List
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.SchemeUrl import SchemeUrl
from entities.resolvers.ScriptDependenciesResolver import ScriptDependenciesResolver
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from utils import file_utils


class ScrapeScriptAndIFrameTestCase(unittest.TestCase):
    headless_browser = None
    browser = None
    PRD = None
    real_results = None
    debug_results = None

    @staticmethod
    def debug_search_all_scripts(headless_browser, url: SchemeUrl) -> List[WebElement]:
        try:
            headless_browser.driver.get(url.string)
        except selenium.common.exceptions.WebDriverException:
            raise
        return headless_browser.driver.find_elements(By.TAG_NAME, 'script')

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        url = SchemeUrl('http://127.0.0.1:3000/')
        url = SchemeUrl('https://corriere.it/')
        # ELABORATION
        PRD = file_utils.get_project_root_directory()
        try:
            cls.headless_browser = FirefoxHeadlessWebDriver(PRD)
        except (FilenameNotFoundError, selenium.common.exceptions.WebDriverException) as e:
            print(f"!!! {str(e)} !!!")
            return
        script_resolver = ScriptDependenciesResolver(cls.headless_browser)
        try:
            cls.interested_scripts = script_resolver.search_script_application_dependencies(url)
        except selenium.common.exceptions.WebDriverException as exc:
            print(f"!!! type={type(exc)}, str={str(exc)} !!!")
            exit(-1)
        try:
            cls.all_scripts = ScrapeScriptAndIFrameTestCase.debug_search_all_scripts(cls.headless_browser, url)
        except selenium.common.exceptions.WebDriverException as exc:
            print(f"!!! type={type(exc)}, str={str(exc)} !!!")
            exit(-1)

    def test_1_debug_prints_of_all_scripts(self):
        print(f"\n------- [1] START DEBUG PRINTS OF ALL SCRIPTS TEST -------")
        count_inline = 0
        for j, script in enumerate(self.all_scripts):
            src = script.get_attribute('src')
            if src == '' or src is None:
                count_inline = count_inline + 1
            print(f"--> script[{j+1}/{len(self.all_scripts)}].src={src}")
        print(f"Number of inline (NO src) scripts = {count_inline}")
        print(f"{len(self.all_scripts)} - {count_inline} = {len(self.all_scripts) - count_inline}")
        print(f"------- [1] END DEBUG PRINTS OF ALL SCRIPTS TEST -------")

    def test_2_debug_prints_of_interested_scripts(self):
        print(f"\n------- [2] START DEBUG PRINTS OF INTERESTED SCRIPTS TEST -------")
        for j, script in enumerate(self.interested_scripts):
            print(f"--> script[{j+1}/{len(self.interested_scripts)}].src={script.src}")
        print(f"------- [2] END DEBUG PRINTS OF INTERESTED SCRIPTS TEST -------")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
