from typing import List, Set
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver


class MainPageScript:
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
    def __init__(self, headless_browser: FirefoxHeadlessWebDriver):
        self.headless_browser = headless_browser

    def search_script_application_dependencies(self, url: str) -> Set[MainPageScript]:
        """
        The method is the actual research of content dependencies from an url/domain name. It searches for dependencies
        of content-type that contains (as a string) one of the value string of the list parameter.


        :param url: A string representing an url.
        :type url: str
        :param values_list: A list of content type value string to be matched.
        :type values_list: List[str]
        :raise selenium.common.exceptions.WebDriverException: There was a problem getting the response form the request.
        :returns: A tuple containing the list of ContentDependencyEntry, and the list of domain name list.
        :rtype: List[ContentDependencyEntry]
        """
        try:
            self.headless_browser.driver.get(url)
            # self.headless_browser.driver.switch_to.
        except selenium.common.exceptions.WebDriverException:
            raise

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
        # self.driver.close()     # close the current window
        self.headless_browser.driver.quit()      # shutdown selenium-wire and then quit the webdriver