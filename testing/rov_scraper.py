import ipaddress
import unittest
from pathlib import Path
import selenium
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.ROVPageScraper import ROVPageScraper
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NotROVStateTypeError import NotROVStateTypeError


class ROVScraperTest(unittest.TestCase):
    headless_browser = None

    @classmethod
    def setUpClass(cls) -> None:
        headless_browser = FirefoxHeadlessWebDriver(project_root_directory=Path.cwd().parent)
        cls.headless_browser = headless_browser
        cls.scraper = ROVPageScraper(True, headless_browser)

    def test_getting_results(self):
        # PARAMS
        as_num = 31034
        # Actual test
        scraper = ROVPageScraper(True, self.headless_browser)
        scraper.load_as_page(as_num)
        try:
            result = scraper.get_prefixes_table_from_page()
        except (ValueError, NotROVStateTypeError, selenium.common.exceptions.NoSuchElementException):
            raise
        print(f"test_getting_results: {len(result)} rows")

    def test_getting_network(self):
        # PARAMS
        as_num = 137
        ip = ipaddress.ip_address('194.119.192.34')
        # Actual test
        scraper = ROVPageScraper(True, self.headless_browser)
        scraper.load_as_page(as_num)
        try:
            row = scraper.get_network_if_present(ip)
        except (ValueError, NotROVStateTypeError, NetworkNotFoundError, selenium.common.exceptions.NoSuchElementException):
            raise
        print(f"test_getting_network: {row.prefix.compressed}")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
