from typing import Set
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.MainFrameScript import MainFrameScript
from entities.SchemeUrl import SchemeUrl


class ScriptDependenciesResolver:
    """
    The class represents an object that provides tools to resolve script dependencies given a HTTP URL.

    ...

    Attributes
    ----------
    headless_browser : FirefoxHeadlessWebDriver
        An instance of a FirefoxHeadlessWebDriver object to use for resolving.

    """
    def __init__(self, headless_browser: FirefoxHeadlessWebDriver):
        """
        Instantiate the object.

        :param headless_browser: An instance of a Firefox headless browser.
        :type headless_browser: FirefoxHeadlessWebDriver
        """
        self.headless_browser = headless_browser

    def search_script_application_dependencies(self, url: SchemeUrl) -> Set[MainFrameScript]:
        """
        The method is the actual research of main frame script dependencies from a HTTP URL.


        :param url: An HTTP URL.
        :type url: SchemeUrl
        :raise selenium.common.exceptions.WebDriverException: There was a problem getting the response form the request.
        :returns: A set of scripts.
        :rtype: Set[MainFrameScript]
        """
        try:
            self.headless_browser.driver.get(url.string)
        except selenium.common.exceptions.WebDriverException:
            raise
        main_page_scripts = set()
        awaiter_scripts = WebDriverWait(self.headless_browser.driver, 10).until(
            expected_conditions.presence_of_all_elements_located((By.XPATH, '//script[not(ancestor::iframe)]'))
        )
        for script in awaiter_scripts:
            src = script.get_attribute('src')
            integrity = script.get_attribute('integrity')
            if integrity == '':
                integrity = None
            if src == '' or src is None:
                pass        # inline script
            else:
                main_page_scripts.add(MainFrameScript(src, integrity))
        return main_page_scripts
