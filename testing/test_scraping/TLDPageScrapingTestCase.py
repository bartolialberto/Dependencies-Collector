import unittest
from pathlib import Path
import selenium
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.scrapers.TLDPageScraper import TLDPageScraper
from exceptions.FilenameNotFoundError import FilenameNotFoundError


class TLDPageScrapingTestCase(unittest.TestCase):
    headless_browser = None

    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == 'LavoroTesi':
                return current
            else:
                current = current.parent

    @classmethod
    def setUpClass(cls) -> None:
        PRD = TLDPageScrapingTestCase.get_project_root_folder()
        try:
            cls.headless_browser = FirefoxHeadlessWebDriver(PRD)
        except (FilenameNotFoundError, selenium.common.exceptions.WebDriverException) as e:
            print(f"!!! {str(e)} !!!")
            return
        cls.tld_page_scraper = TLDPageScraper(cls.headless_browser)

    def test_1_scraping_tlds(self):
        try:
            self.tld_page_scraper.scrape_tld()
        except (selenium.common.exceptions.WebDriverException, selenium.common.exceptions.NoSuchElementException) as e:
            print(f"!!! {str(e)} !!!")
            return
        print(f"TLDs list contains {len(self.tld_page_scraper.tld_list)} elements\n")
        for i, tld in enumerate(self.tld_page_scraper.tld_list):
            print(f"[{i+1}/{len(self.tld_page_scraper.tld_list)}] = {tld}")
        print(f"\nTLDs list contains {len(self.tld_page_scraper.tld_list)} elements")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.headless_browser.close()


if __name__ == '__main__':
    unittest.main()
