from typing import List, Tuple
import selenium
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Firefox
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from exceptions.ReachedDOMRootError import ReachedDOMRootError
from utils import string_utils, list_utils
from selenium.webdriver.support import expected_conditions as ec


class ContentDependencyEntry:
    """
    This class represent a personalized entry of content dependency.

    ...

    Attributes
    ----------
    domain_name : `str`
        The domain name.
    url : `str`
        The url.
    response_code : `int`
        The response code of the request.
    mime_type : `str`
        The mime type of the content.
    """

    def __init__(self, domain_name: str, url: str, response_code: int, mime_type: str):
        """
        Initialized an object.

        :param domain_name: The domain name.
        :type domain_name: str
        :param url: The url.
        :type url: str
        :param response_code: The response code of the request.
        :type response_code: int
        :param mime_type: The mime type of the content.
        :type mime_type: str
        """
        self.domain_name = domain_name
        self.url = url
        self.response_code = response_code
        self.mime_type = mime_type

    def __str__(self) -> str:
        sep = '\t'
        return f"{self.domain_name}{sep}{self.url}{sep}{self.response_code}{sep}{self.mime_type}"

    def __eq__(self, other) -> bool:
        if isinstance(other, ContentDependencyEntry):
            return self.url == other.url and self.mime_type == other.mime_type
        else:
            return False


class MainPageScript:
    def __init__(self, src: str, integrity: str or None):
        self.src = src
        self.integrity = integrity

    def __str__(self):
        return f"MainPageScript: src={self.src}, integrity={self.integrity}"


class ContentDependenciesResolver:
    """
    This class concern is to search for content dependencies to render/view/elaborate a certain url. Requires a valid
    headless browser to work associated to geckodriver. In particular geckodriver executable needs to be placed in the
    input folder of the project root folder (PRD).

    ...

    Attributes
    ----------
    headless_browser : FirefoxHeadlessWebDriver
        An instance of a headless browser, in particular Firefox.
    """

    def __init__(self, headless_browser: FirefoxHeadlessWebDriver):
        """
        Self-explanatory.


        :param headless_browser: The instance of a Firefox headless browser.
        :type headless_browser: FirefoxHeadlessWebDriver
        """
        self.headless_browser = headless_browser

    def search_script_application_dependencies(self, url: str, values_list: List[str]) -> Tuple[List[ContentDependencyEntry], List[MainPageScript]]:
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
        # print(f"DEBUG: {len(self.headless_browser.driver.window_handles)} tabs opened...")
        # response.raise_for_status()
        content_dependencies = list()
        for request in self.headless_browser.driver.requests:
            if request.response:
                if request.response.headers["Content-Type"] is not None:
                    if string_utils.multiple_contains(request.response.headers['Content-Type'], values_list):
                        #content_dependencies.append(ContentDependencyEntry(request.host, request.url, request.response.status_code, request.response.headers['Content-Type']))
                        list_utils.append_with_no_duplicates(content_dependencies, ContentDependencyEntry(request.host, request.url, request.response.status_code, request.response.headers['Content-Type']))
                    else:
                        pass    # there is no javascript/application Content-Type header
                else:
                    pass    # there is no Content-Type header
            else:
                pass    # there is no response

        # TODO: trovare degli esempi per verificare tutto il funzionamento correttamente (siti con iframe che contengono script)
        main_page_scripts = list()
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
                main_page_scripts.append(MainPageScript(src, integrity))





        """
        all_elem = WebDriverWait(self.headless_browser.driver, 10).until(
          lambda driver: driver.find_elements(By.XPATH, '//*[not(self::iframe)]')
        )
        for i, elem in enumerate(all_elem):
            print(f"elem[{i+1}/{len(all_elem)}]: {elem.tag_name}, src={elem.get_attribute('src')}")
        """


        """
        main_page_scripts = list()
        for i, iframe in enumerate(iframes):
            print(f"iframe[{i + 1}/{len(iframes)}]: src={iframe.get_attribute('src')}")
            iframe_scripts = iframe.find_elements(By.TAG_NAME, 'script')
            for iframe_script in iframe_scripts:
                main_page_scripts.append(iframe_script)
        for i, script in enumerate(main_page_scripts):
            print(f"iframe_script[{i + 1}/{len(main_page_scripts)}]: src={script.get_attribute('src')}")
        """

        """
        scripts = WebDriverWait(self.headless_browser.driver, 10).until(
            # lambda driver: driver.find_elements(By.XPATH, '//iframe/script')
            # lambda driver: driver.find_elements(By.XPATH, '//script[ancestor::*[not(self::iframe)]]')
            # lambda driver: driver.find_elements(By.XPATH, '//script[ancestor::*[iframe]]')
            lambda driver: driver.find_elements(By.XPATH, 'iframe[descendant::script]')
            # lambda driver: driver.find_elements(By.XPATH, '//iframe')
            # lambda driver: driver.find_elements(By.XPATH, '//script')
            #
            #
            # lambda driver: driver.find_elements(By.TAG_NAME, 'script')
            # lambda driver: driver.find_elements(By.TAG_NAME, 'iframe')
        )
        for i, script in enumerate(scripts):
            is_integrity = False
            integrity = script.get_attribute('integrity')
            if integrity is None or integrity == '':
                is_integrity = False
            else:
                is_integrity = True
            src = script.get_attribute('src')
            mime_type = script.get_attribute('type')
            print(f"script[{i+1}/{len(scripts)}] = (integrity={integrity}, src={src}, type={mime_type})")
        """



        """
        scripts = self.headless_browser.driver.find_elements(By.TAG_NAME, 'script')
        for i, script in enumerate(scripts):
            is_integrity = False
            integrity = script.get_attribute('integrity')
            if integrity is None or integrity == '':
                is_integrity = False
            else:
                is_integrity = True
            src = script.get_attribute('src')

            is_in_iframe = False
            try:
                iframe = ContentDependenciesResolver.try_to_get_iframe_parent(script)
                is_in_iframe = True
            except ReachedDOMRootError:
                is_in_iframe = False

            if src is None or src == '':
                print(f"script[{i+1}/{len(scripts)}] = (integrity={is_integrity}, iframe={is_in_iframe}, INLINE script with length {len(script.get_attribute('textContent'))})")
            else:
                print(f"script[{i + 1}/{len(scripts)}] = (integrity={is_integrity}, iframe={is_in_iframe}, src={src})")

        # Prove di elaborazioni da tenere per il futuro che potrebbero essere utili
        #iframes = self.headless_browser.driver.find_elements(By.TAG_NAME, 'iframe')
        #self.headless_browser.driver.switch_to.frame(iframe)
        #self.headless_browser.driver.switch_to.default_content()

        #iframes_awaiter = WebDriverWait(self.headless_browser.driver, 10).until(
            #ec.presence_of_element_located((By.TAG_NAME, 'iframe'))
        #)

        #iframes = WebDriverWait(self.headless_browser.driver, 10).until(
            #lambda driver: driver.find_elements(By.XPATH, '/iframe/script')
            #ec.visibility_of_element_located((By.XPATH, '/iframe/script'))
        #)

        #iframes = WebDriverWait(self.headless_browser.driver, 10).until(
            #lambda driver: driver.find_elements(By.TAG_NAME, 'iframe')
        #)

        #iframes = WebDriverWait(self.headless_browser.driver, 10).until(
            #lambda driver: driver.find_elements(By.XPATH, '/iframe/script')
            #ec.visibility_of_element_located((By.XPATH, '/iframe/script'))
        #)
        """

        return content_dependencies, main_page_scripts

    def test(self, url: str):
        try:
            self.headless_browser.driver.get(url)
            # self.headless_browser.driver.switch_to.
        except selenium.common.exceptions.WebDriverException:
            raise
        scripts = WebDriverWait(self.headless_browser.driver, 10).until(
            lambda driver: driver.find_elements(By.TAG_NAME, 'script')
        )
        return scripts

    def close(self):
        """
        This method closes the headless browser process.

        """
        # self.driver.close()     # close the current window
        self.headless_browser.driver.quit()      # shutdown selenium-wire and then quit the webdriver

    @staticmethod
    def try_to_get_iframe_parent(element: WebElement) -> WebElement:
        candidate = element
        try:
            candidate = candidate.find_element(By.XPATH, '..')
        except WebDriverException:
            raise ReachedDOMRootError
        if isinstance(candidate, Firefox):
            raise ReachedDOMRootError
        else:
            pass
        while candidate.tag_name != 'iframe':
            try:
                candidate = candidate.find_element(By.XPATH, '..')
            except WebDriverException:
                raise ReachedDOMRootError
            if isinstance(candidate, Firefox):
                raise ReachedDOMRootError
            else:
                pass
        return candidate
