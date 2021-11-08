import os
from pathlib import Path
from typing import List
import selenium
from selenium.webdriver.firefox.options import Options
from seleniumwire import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import re
from utils import list_utils, domain_name_utils, file_utils


class ContentDependencyEntry:
    domain_name: str
    url: str
    response_code: int
    mime_type: str

    def __init__(self, domain_name: str, url: str, response_code: int, mime_type: str):
        self.domain_name = domain_name
        self.url = url
        self.response_code = response_code
        self.mime_type = mime_type


class FirefoxContentDependenciesResolver:
    firefox_path: str
    gecko_driver_path: str
    options: Options
    binary: FirefoxBinary
    driver: webdriver.Firefox

    def __init__(self, firefox_path="C:\\Program Files\\Mozilla Firefox\\firefox.exe", gecko_driver_path="input/geckodriver.exe"):
        cwd = Path.cwd()        # TODO: gestire la ricerca della cartella con un metodo in utils..
        input_folder = None
        for folder in cwd.iterdir():
            if folder.is_dir() and folder.name == "input":
                input_folder = folder
                break
        if input_folder is None:
            input_folder = Path("input")
            input_folder.mkdir(parents=True, exist_ok=False)
            # crea dal parent la cartella input
            raise ValueError()
        for file in input_folder.iterdir():
            if file.is_file() and file_utils.parse_file_extension(file.name) == ".exe":     # TODO: ma se è linux o mac ... ?
                self.gecko_driver_path = f"input/{file.name}"
                break
            else:
                self.gecko_driver_path = "input/geckodriver.exe"
                break
        self.firefox_path = firefox_path
        try:
            self.init_headless_browser()
        except selenium.common.exceptions.WebDriverException:
            raise

    def init_headless_browser(self):
        options = Options()
        options.headless = True
        self.options = options
        self.binary = FirefoxBinary(self.firefox_path)
        try:
            self.driver = webdriver.Firefox(executable_path=self.gecko_driver_path, options=self.options, firefox_binary=self.binary)
        except selenium.common.exceptions.WebDriverException:
            raise
        print("Headless browser initialize correctly.")

    def search_domain_dependencies(self, string: str) -> List[str]:
        url = domain_name_utils.deduct_url(string)
        mat = re.findall("/", url)
        if len(mat) == 2:
            match = re.search("//(.*)", url)
            boundaries = match.span()
            url_domain = url[boundaries[0] + 2:boundaries[1]]
        else:
            match = re.search("//(.*?)/", url)
            boundaries = match.span()
            url_domain = url[boundaries[0] + 2:boundaries[1] - 1]
        print("Looking for software dependencies of domain: ", url_domain)
        content_dependencies, domain_list = self.search_dependencies(url)
        try:
            for domain in domain_list:
                if domain == url_domain:
                    domain_list.remove(domain)
        except Exception as e:
            print("Error: ", e)
        return domain_list

    def search_dependencies(self, string: str) -> tuple:
        url = domain_name_utils.deduct_url(string)
        print(f"Searching content dependencies for: {url}")
        # Go to the url home page
        try:
            self.driver.get(url)
        except selenium.common.exceptions.WebDriverException as e:
            print("!!! Error while getting the response !!!")
            raise
        domain_list = list()
        content_dependencies = list()
        for request in self.driver.requests:
            if request.response.headers["Content-Type"] != None:
                if "javascript" in request.response.headers['Content-Type'] or "application/" in request.response.headers['Content-Type']:
                    content_dependencies.append(ContentDependencyEntry(request.host, request.url, request.response.status_code, request.response.headers['Content-Type']))
                    list_utils.append_with_no_duplicates(domain_list, request.host)
        print(f"javascript/application dependencies found: {len(content_dependencies)} on {len(domain_list)} domains.")
        return content_dependencies, domain_list

    def close(self):
        self.driver.quit()      # shutdown selenium-wire and then quit the webdriver
        # self.driver.close()     # close the current window
        # self.binary.kill()      # kill the browser (if it's stuck)
