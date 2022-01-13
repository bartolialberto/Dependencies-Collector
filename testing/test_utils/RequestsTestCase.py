import os
import unittest
from pathlib import Path
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from selenium.webdriver.support import expected_conditions as ec


class RequestsTestCase(unittest.TestCase):
    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == 'LavoroTesi':
                return current
            else:
                current = current.parent

    def test_getting_all_tlds(self):
        PRD = RequestsTestCase.get_project_root_folder()
        headless_browser = FirefoxHeadlessWebDriver(project_root_directory=PRD)
        try:
            headless_browser.driver.get('https://www.iana.org/domains/root/db')
        except selenium.common.exceptions.WebDriverException:
            raise
        tld_table = WebDriverWait(headless_browser.driver, 10).until(
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
        print(f"DEBUG: len(trs) = {len(trs)}")
        tld_list = list()
        for i, tr in enumerate(trs):

            try:
                a = tr.find_element(By.TAG_NAME, "a")
                tld_list.append(a.text)
            except selenium.common.exceptions.NoSuchElementException:
                headless_browser.close()
                raise


            '''
            try:
                td = tr.find_element(By.TAG_NAME, "td")
                try:
                    span = td.find_element(By.TAG_NAME, "span")
                    try:
                        a = span.find_element(By.TAG_NAME, "a")
                        tld_list.append(a.text)
                    except selenium.common.exceptions.NoSuchElementException:
                        headless_browser.close()
                        raise
                except selenium.common.exceptions.NoSuchElementException:
                    headless_browser.close()
                    raise
            except selenium.common.exceptions.NoSuchElementException:
                headless_browser.close()
                raise
            '''

        print(f"DEBUG: len(tld_list) = {len(tld_list)}")
        headless_browser.close()

        file = Path(f"{str(PRD)}{os.sep}output{os.sep}tlds.txt")
        try:
            with open(str(file), 'w') as f:  # 'w' or 'x'
                for tld in tld_list:
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


if __name__ == '__main__':
    unittest.main()
