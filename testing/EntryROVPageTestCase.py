import ipaddress
import unittest
from pathlib import Path
import selenium
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.ROVPageScraper import ROVPageScraper
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError


class EntryROVPageTestCase(unittest.TestCase):
    headless_browser = None
    scraper = None
    as_number = None

    @classmethod
    def setUpClass(cls) -> None:
        headless_browser = FirefoxHeadlessWebDriver(project_root_directory=Path.cwd().parent)
        cls.headless_browser = headless_browser
        cls.scraper = ROVPageScraper(headless_browser)

    def setUp(self) -> None:
        # PARAM
        self.as_number = 10886
        self.ip = ipaddress.ip_address('199.7.91.13')

    def test_getting_row_table_from_ip(self):
        print(f"test_getting_row_table_from_ip ****************************************************************")
        print(f"Querying page of AS{self.as_number} and IP = {self.ip.compressed}")
        try:
            self.scraper.load_as_page(self.as_number)
            try:
                row = self.scraper.get_network_if_present(self.ip)
                print(f"--> Found row: {str(row)}")
            except (NetworkNotFoundError, TableEmptyError, ValueError, NotROVStateTypeError, selenium.common.exceptions.NoSuchElementException) as exc:
                print(f"!!! {str(exc)} !!!")
        except selenium.common.exceptions.WebDriverException as exc:
            print(f"!!! {str(exc)} !!!")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
