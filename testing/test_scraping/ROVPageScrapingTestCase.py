import ipaddress
import unittest
from pathlib import Path
import selenium
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.scrapers.ROVPageScraper import ROVPageScraper
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError
from persistence.BaseModel import project_root_directory_name


class ROVPageScrapingTestCase(unittest.TestCase):
    headless_browser = None

    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == project_root_directory_name:
                return current
            else:
                current = current.parent

    @classmethod
    def setUpClass(cls) -> None:
        PRD = ROVPageScrapingTestCase.get_project_root_folder()
        try:
            cls.headless_browser = FirefoxHeadlessWebDriver(PRD)
        except (FilenameNotFoundError, selenium.common.exceptions.WebDriverException) as e:
            print(f"!!! {str(e)} !!!")
            raise Exception
        cls.rov_page_scraper = ROVPageScraper(cls.headless_browser)

    def test_1_getting_the_entire_table(self):
        print(f"\n------- [1] START GETTING ENTIRE TABLE FROM AS PAGE -------")
        # PARAMETERS
        as_number = 137
        # ELABORATION
        try:
            self.rov_page_scraper.load_as_page(as_number)
        except (TableNotPresentError, ValueError, TableEmptyError, NotROVStateTypeError, selenium.common.exceptions.WebDriverException) as exc:
            print(f"!!! {str(exc)} !!!")
            return
        for i, row in enumerate(self.rov_page_scraper.prefixes_table):
            print(f"row[{i+1}/{len(self.rov_page_scraper.prefixes_table)}]: {str(row)}")
        self.assertNotEqual(0, len(self.rov_page_scraper.prefixes_table))
        print(f"------- [1] END GETTING ENTIRE TABLE FROM AS PAGE -------")

    def test_2_is_ip_in_a_network_of_the_page(self):
        print(f"\n------- [2] START NETWORK IF PRESENT FROM ADDRESS FROM AS PAGE TEST -------")
        # PARAMETERS
        ip = ipaddress.IPv4Address('199.7.63.13')
        # ELABORATION
        try:
            row = self.rov_page_scraper.get_network_if_present(ip)
        except (TableNotPresentError, TableEmptyError, NetworkNotFoundError) as exc:
            print(f"!!! {str(exc)} !!!")
            return
        print(f"ROW FOUND: {str(row)}")
        self.assertIsNotNone(row)
        print(f"------- [2] END NETWORK IF PRESENT FROM ADDRESS FROM AS PAGE TEST -------")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
