from pathlib import Path
from typing import List, Tuple
import selenium
from selenium.webdriver.firefox.options import Options
from seleniumwire import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import re
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from utils import list_utils, domain_name_utils, file_utils


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


class FirefoxContentDependenciesResolver:
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

    def __init__(self, firefox_path="C:\\Program Files\\Mozilla Firefox\\firefox.exe"):
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
        try:
            # TODO: ma se è linux o mac ... ?
            result = file_utils.search_for_file_type_in_subdirectory("input", ".exe")
        except FilenameNotFoundError:
            raise
        gecko_driver_file = result[0]
        self.gecko_driver_path = str(gecko_driver_file)
        self.firefox_path = firefox_path
        try:
            options = Options()
            options.headless = True
            self.options = options
            self.binary = FirefoxBinary(self.firefox_path)
            try:
                self.driver = webdriver.Firefox(executable_path=self.gecko_driver_path, options=self.options,
                                                firefox_binary=self.binary)
            except selenium.common.exceptions.WebDriverException:
                raise
            self.driver.implicitly_wait(10)     # SAFETY
            print("Headless browser initialized correctly.")
        except selenium.common.exceptions.WebDriverException:
            raise

    def search_script_application_dependencies(self, string: str) -> Tuple[List[ContentDependencyEntry], List[str]]:
        """
        The method is the actual research of content dependencies from an url/domain name.

        :param string: A string representing an url or a domain name. The latter will be changed to a https url.
        :type string: str
        :raise selenium.common.exceptions.WebDriverException: There was a problem getting the response form the request.
        :returns: A tuple containing the list of ContentDependencyEntry, and the list of domain name list.
        :rtype: Tuple[List[ContentDependencyEntry], List[str]]
        """
        url = domain_name_utils.deduct_http_url(string)
        print(f"Searching content dependencies for: {url}")
        try:
            self.driver.get(url)
        except selenium.common.exceptions.WebDriverException:
            raise
        domain_list = list()
        content_dependencies = list()
        for request in self.driver.requests:
            if request.response.headers["Content-Type"] is not None:
                if "javascript" in request.response.headers['Content-Type'] or "application/" in request.response.headers['Content-Type']:
                    content_dependencies.append(ContentDependencyEntry(request.host, request.url, request.response.status_code, request.response.headers['Content-Type']))
                    list_utils.append_with_no_duplicates(domain_list, request.host)
        self.driver.requests.clear()
        return content_dependencies, domain_list

    def close(self):
        """
        This method closes the headless browser process.

        """
        # self.driver.close()     # close the current window
        self.driver.quit()      # shutdown selenium-wire and then quit the webdriver
