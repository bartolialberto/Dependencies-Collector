from pathlib import Path
import selenium
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from seleniumwire import webdriver
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import file_utils


class FirefoxHeadlessWebDriver:

    def __init__(self, project_root_directory=Path.cwd()):
        try:
            # TODO: ma se è linux o mac ... ?
            result = file_utils.search_for_file_type_in_subdirectory("input", ".exe", project_root_directory)
        except FileWithExtensionNotFoundError:
            raise
        gecko_driver_file = result[0]
        self.gecko_driver_path = str(gecko_driver_file)     # abs path
        options = Options()
        options.headless = True
        self.options = options
        try:
            self.service = Service(self.gecko_driver_path)
            # self.binary = FirefoxBinary(firefox_path)     # deprecated
        except selenium.common.exceptions.WebDriverException:
            raise
        try:
            # self.driver = webdriver.Firefox(executable_path=self.gecko_driver_path, options=self.options, firefox_binary=self.binary)
            self.driver = webdriver.Firefox(service=self.service, options=self.options)
        except selenium.common.exceptions.WebDriverException:
            raise
        self.driver.implicitly_wait(10)  # SAFETY

    def close(self):
        # self.driver.close()     # close the current window
        self.driver.quit()      # shutdown selenium-wire and then quit the webdriver
