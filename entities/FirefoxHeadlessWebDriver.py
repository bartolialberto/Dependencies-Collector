from pathlib import Path
import selenium
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from seleniumwire import webdriver
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from utils import file_utils


class FirefoxHeadlessWebDriver:
    """
    This class create an instance of a headless firefox web driver using geckodriver and a valid installation of
    Firefox.

    ...

    Attributes
    ----------
    gecko_driver_path : str
        The filepath of the geckodriver executable if found.
    options : selenium.webdriver.firefox.options.Options
        Instance of an object representing the options associated to the firefox headless browser.
    service : selenium.webdriver.firefox.service.Service
        Object needed to run the headless browser.
    driver : seleniumwire.webdriver.Firefox
        Actual object of the web driver.
    """

    def __init__(self, project_root_directory=Path.cwd()):
        """
        Requires the project root directory (PRD) to find the geckodriver executable in the input sub-folder of the PRD.
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
        (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
        returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
        return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is
        set to default as if the entry point is main.py file (which is the only entry point considered).

        :param project_root_directory: The Path object pointing at the project root directory.
        :type project_root_directory: Path
        :raise FilenameNotFoundError: If the geckodriver executable is not found.
        :raise selenium.common.exceptions.WebDriverException: If there's a problem initializing the service object or
        the webdriver object.
        """
        try:
            # TODO: ma se è linux o mac ... ?
            result = file_utils.search_for_filename_in_subdirectory('input', 'geckodriver.exe', project_root_directory)
        except FilenameNotFoundError:
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
        self.driver.set_page_load_timeout(30)       # [s]
        self.driver.implicitly_wait(10)  # SAFETY

    def close(self) -> None:
        """
        Shutdown seleniumwire and then quit the webdriver.

        """
        # self.driver.close()     # close the current window
        self.driver.quit()      # shutdown selenium-wire and then quit the webdriver

    def close_and_reopen(self) -> None:
        self.close()
        try:
            self.service = Service(self.gecko_driver_path)
        except selenium.common.exceptions.WebDriverException:
            raise
        try:
            self.driver = webdriver.Firefox(service=self.service, options=self.options)
        except selenium.common.exceptions.WebDriverException:
            raise
        self.driver.set_page_load_timeout(30)  # [s]
        self.driver.implicitly_wait(10)  # SAFETY
