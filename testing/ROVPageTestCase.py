import unittest
from pathlib import Path
import selenium
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.scrapers.ROVPageScraper import ROVPageScraper
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError


class ROVPageTestCase(unittest.TestCase):
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
        self.as_numbers = [10886, 7500, 137]

    def test_getting_networks(self):
        print(f"test_getting_networks ****************************************************************")
        for as_number in self.as_numbers:
            try:
                self.scraper.load_as_page(as_number)
                print(f"Networks scraped from AS{as_number}:")
                for i, row in enumerate(self.scraper.prefixes_table):
                    print(f"--> [{i+1}/{len(self.scraper.prefixes_table)}]: {str(row)}")
            except (ValueError, selenium.common.exceptions.WebDriverException, TableNotPresentError, TableEmptyError, NotROVStateTypeError) as e:
                print(f"!!! {str(e)} !!!")
            print('')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
