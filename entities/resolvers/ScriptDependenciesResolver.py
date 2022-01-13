from typing import List, Set
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver


class MainPageScript:
    """
    This class represents a very simple container that contains infos representating a script and its withdraw.

    ...

    Attributes
    ----------
    src : str
        The src attribute value of the script HTML element.
    integrity : str or None
        The integrity attribute value of the script HTML. None is for absence.
    """
    def __init__(self, src: str, integrity: str or None):
        self.src = src
        self.integrity = integrity

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if isinstance(other, MainPageScript):
            if self.src == other.src:
                return True
            else:
                return False
        else:
            return False

    def __str__(self):
        return f"MainPageScript: src={self.src}, integrity={self.integrity}"


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

    def search_script_application_dependencies(self, url: str) -> Set[MainPageScript]:
        """
        The method is the actual research of script dependencies from a HTTP URL.


        :param url: An HTTP URL.
        :type url: str
        :raise selenium.common.exceptions.WebDriverException: There was a problem getting the response form the request.
        :returns: A set of scripts.
        :rtype: Set[MainPageScript]
        """
        try:
            self.headless_browser.driver.get(url)
        except selenium.common.exceptions.WebDriverException:
            raise

        # TODO: trovare il modo definitivo per trovare il tipo di script voluto
        # TODO: trovare degli esempi per verificare tutto il funzionamento correttamente (siti con iframe che contengono script)
        main_page_scripts = set()
        awaiter_scripts = WebDriverWait(self.headless_browser.driver, 10).until(
          lambda driver: driver.find_elements(By.TAG_NAME, 'script')
        )
        for awaiter_script in awaiter_scripts:
            src = awaiter_script.get_attribute('src')
            integrity = awaiter_script.get_attribute('integrity')
            if integrity == '':
                integrity = None
            if src is None:
                pass    # inline script
            elif src == '':
                pass    # script in iframe
            else:
                main_page_scripts.add(MainPageScript(src, integrity))
        return main_page_scripts

    def close(self):
        self.headless_browser.driver.quit()