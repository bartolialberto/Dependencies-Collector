from typing import List, Tuple
import selenium
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver


# TODO: rifare tutta la doc
class ContentDependencyEntry:
    """
    This class represent a personalized entry of content dependency.

    ...

    Instance Attributes
    -------------------
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
    This class concern is to start a headless browser and then, given an url, search for content dependencies to render
    that url, in particular dependencies of type javascript and application/*. The headless browser needs a valid
    installation of firefox with its executable file path, and geckodriver executable put in the input folder of the
    project root folder.

    ...

    Attributes
    ----------
    firefox_path : `str`
        The firefox.exe file path (absolute).
    gecko_driver_path : `str`
        The geckodriver.exe file path (absolute or relative).
    options : `selenium.webdriver.firefox.options.Options`
        Instance of the object representating the options in the browser.
    binary : `selenium.webdriver.firefox.firefox_binary.FirefoxBinary`
        Instance of Firefox binary.
    driver : `seleniumwire.webdriver.Firefox`
        Instance of the Firefox driver.
    """

    def __init__(self, headless_browser: FirefoxHeadlessWebDriver):
        """
        This class concern is to start a headless browser and then, given an url, search for content dependencies to
        render that url, in particular dependencies of type javascript and application/*. The headless browser needs a
        valid installation of firefox with its executable file path, and geckodriver executable put in the input folder
        of the project root folder. The method is the actual starting point of the headless browser. If everything goes
        well, then the headless browser is set as attribute.


        :param firefox_path : The firefox.exe file path (absolute).
        :type firefox_path: str
        :raise FilenameNotFoundError: The geckodriver file is not found.
        :raise selenium.common.exceptions.WebDriverException: There was a problem starting the firefox webdriver.
        """
        self.headless_browser = headless_browser

    def search_script_application_dependencies(self, url: str) -> List[ContentDependencyEntry]:
        """
        The method is the actual research of content dependencies from an url/domain name.

        :param string: A string representing an url or a domain name. The latter will be changed to a https url.
        :type string: str
        :raise selenium.common.exceptions.WebDriverException: There was a problem getting the response form the request.
        :returns: A tuple containing the list of ContentDependencyEntry, and the list of domain name list.
        :rtype: Tuple[List[ContentDependencyEntry], List[str]]
        """
        try:
            self.headless_browser.driver.get(url)
        except selenium.common.exceptions.WebDriverException:
            raise
        # response.raise_for_status()     # TODO: mmm solo fare una stampa e ritornare? Meglio va..
        content_dependencies = list()
        for request in self.headless_browser.driver.requests:
            if request.response:
                if request.response.headers["Content-Type"] is not None:
                    if "javascript" in request.response.headers['Content-Type'] or "application/" in request.response.headers['Content-Type']:
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
