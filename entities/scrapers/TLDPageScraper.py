from pathlib import Path
from typing import List
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from utils import file_utils, domain_name_utils


class TLDPageScraper:
    """
    This class represents a tool to use for resolving all the existent Top-Level Domains.
    In particular it is a scraper that looks for the 'tld-table' (id of html element) table in the page:
            https://www.iana.org/domains/root/db
    Requires a valid headless browser to work associated to geckodriver.
    In particular geckodriver executable needs to be placed in the 'input' folder of the project root folder (PRD).

    ...

    Attributes
    ----------
    headless_browser : FirefoxHeadlessWebDriver
        An instance of a headless browser, in particular Firefox.
    tld_list : List[str]
        An attribute that contains all the Top-Level Domains.
    """
    def __init__(self, headless_browser: FirefoxHeadlessWebDriver):
        """
        Initialize object.

        :param headless_browser: The instance of a Firefox headless browser.
        :type headless_browser: FirefoxHeadlessWebDriver
        """
        self.headless_browser = headless_browser
        self.tld_list = list()

    def scrape_tld(self) -> List[str]:
        """
        This method is the actual execution of the scraping.

        :raise selenium.common.exceptions.WebDriverException: If there is getting the web page.
        :raise selenium.common.exceptions.NoSuchElementException: If the web page is not formatted as usual: the DOM
        traversing needs to be modified.
        :return: The list of Top-Level Domains, that are also saved in the 'tld_list' attribute'.
        :rtype: List[str]
        """
        try:
            self.headless_browser.driver.get('https://www.iana.org/domains/root/db')
        except selenium.common.exceptions.WebDriverException:
            raise
        tld_table = WebDriverWait(self.headless_browser.driver, 10).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="tld-table"]'))
        )
        try:
            tbody = tld_table.find_element(By.TAG_NAME, "tbody")
        except selenium.common.exceptions.NoSuchElementException:
            raise
        try:
            trs = tbody.find_elements(By.TAG_NAME, "tr")
        except selenium.common.exceptions.NoSuchElementException:
            raise
        for i, tr in enumerate(trs):
            try:
                a = tr.find_element(By.TAG_NAME, "a")
                self.tld_list.append(domain_name_utils.insert_trailing_point(a.text[1:]))       # from '.it' to 'it.'
            except selenium.common.exceptions.NoSuchElementException:
                raise
        return self.tld_list

    def import_from_txt(self, filepath: str) -> List[str]:
        """
        This method parses a .txt file and consider each line of the file as a TLD.

        :param filepath: The absoulte path of the .txt file.
        :type filepath: str
        :raise ValueError: If there is a problem opening the file.
        :raise PermissionError: If there is a problem opening the file.
        :raise FileNotFoundError: If there is a problem opening the file.
        :raise OSError: If there is a problem opening the file.
        :return: The list od TLDs.
        :rtype: List[str]
        """
        try:
            f = open(filepath, "r")
            for line in f:
                # self.tld_list.append(domain_name_utils.insert_trailing_point(line[1:]))
                self.tld_list.append(line)
            f.close()
            return self.tld_list
        except ValueError:
            raise
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise

    @staticmethod
    def import_txt_from_input_folder(filename='tlds.txt', project_root_folder=Path.cwd()) -> List[str]:
        """
        This static method parses a .txt file from the 'input' folder and consider each line of the file as a TLD.

        :param filename: The filename (with extension) to load.
        :type filename: str
        :param project_root_folder: The Path object pointing at the project root directory.
        :type project_root_folder: Path
        :raise FileNotFoundError: If the file is not found.
        :raise ValueError: If there is a problem opening the file.
        :raise PermissionError: If there is a problem opening the file.
        :raise FileNotFoundError: If there is a problem opening the file.
        :raise OSError: If there is a problem opening the file.
        :return: The list od TLDs.
        :rtype: List[str]
        """
        try:
            result = file_utils.search_for_filename_in_subdirectory('input', filename, project_root_folder)
        except FileNotFoundError:
            raise
        file = result[0]
        tlds = list()
        try:
            f = open(str(file), "r")
            for line in f:
                # tlds.append(domain_name_utils.insert_trailing_point(line[1:]))
                tlds.append(line)
            f.close()
        except ValueError:
            raise
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise
        return tlds

    def export_txt(self, filepath: str) -> None:
        """
        This method exports the TLD list into a .txt file located from the filepath parameter.

        :param filepath: the filepath to the file.
        :type filepath: str
        :raise PermissionError: If there's a problem with the file.
        :raise FileNotFoundError: If the file is not found.
        :raise OSError: If there's a problem with the file.
        """
        try:
            with open(filepath, 'w') as f:  # 'w' or 'x'
                for tld in self.tld_list:
                    try:
                        f.write(f"{tld}\n")
                    except UnicodeEncodeError:
                        pass
                f.close()
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise
