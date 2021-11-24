from typing import List, Tuple
import selenium
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from utils import string_utils


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

    def __str__(self):
        sep = '\t'
        return f"{self.domain_name}{sep}{self.url}{sep}{self.response_code}{sep}{self.mime_type}"


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

    def search_script_application_dependencies(self, url: str, values_list: List[str]) -> List[ContentDependencyEntry]:
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
        except selenium.common.exceptions.WebDriverException:
            raise
        # response.raise_for_status()
        content_dependencies = list()
        for request in self.headless_browser.driver.requests:
            if request.response:
                if request.response.headers["Content-Type"] is not None:
                    if string_utils.multiple_contains(request.response.headers['Content-Type'], values_list):
                        content_dependencies.append(ContentDependencyEntry(request.host, request.url, request.response.status_code, request.response.headers['Content-Type']))
                        # list_utils.append_with_no_duplicates(domain_list, request.host)
                    else:
                        pass    # there is no javascript/application Content-Type header
                else:
                    pass    # there is no Content-Type header
            else:
                pass    # there is no response
        return content_dependencies

    def close(self):
        """
        This method closes the headless browser process.

        """
        # self.driver.close()     # close the current window
        self.headless_browser.driver.quit()      # shutdown selenium-wire and then quit the webdriver
