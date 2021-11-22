import ipaddress
from typing import List
import selenium
from selenium.webdriver.common.by import By
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.ROVStates import ROVStates
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NotROVStateTypeError import NotROVStateTypeError


class RowPrefixesTable:
    def __init__(self, as_number: str, prefix: str, span: str, cc: str, visibility: str, rov_state: str, roas: str):
        tmp = as_number.strip('AS')
        try:
            int_as_number = int(tmp)
        except ValueError:
            raise
        if int_as_number >= 0:
            self.as_number = int_as_number
        else:
            raise ValueError()
        try:
            self.prefix = ipaddress.ip_network(prefix)
        except ValueError:
            raise
        tmp = span.replace(',', '')
        try:
            int_span = int(tmp)
        except ValueError:
            raise
        if int_span >= 0:
            self.span = int_span
        else:
            raise ValueError()
        if len(cc) == 2:
            self.cc = cc
        else:
            raise ValueError()
        try:
            int_visibility = int(visibility)
        except ValueError:
            raise
        if int_visibility >= 0:
            self.visibility = int_visibility
        else:
            raise ValueError()
        try:
            enum_rov_state = ROVStates.parse_from_string(rov_state)
            self.rov_state = enum_rov_state
        except NotROVStateTypeError:
            raise
        self.roas = roas

    def __str__(self):
        return f"[AS{self.as_number}\t{self.prefix.compressed}\t{str(self.span)}\t{self.cc}\t{str(self.visibility)}\t{self.rov_state.to_string()}\t{self.roas}]"


class ROVPageScraper:
    def __init__(self, dbg: bool, headless_browser: FirefoxHeadlessWebDriver):      # TODO: dbg inutile
        self.headless_browser = headless_browser
        self.page_loaded = False
        self.sleep_time = 30
        self.dbg = dbg

    def load_page(self, url_page: str):
        try:
            self.headless_browser.driver.get(url_page)
        except selenium.common.exceptions.WebDriverException:
            raise
        self.page_loaded = True
        # self.__wait_for_scripts()
        #self.__scrape_table()
        #self.get_prefixes_table_from_page()

    def load_as_page(self, as_number: int):
        self.load_page(ROVPageScraper.base_url(as_number))

    # TODO: e se la tabella è vuota?
    def get_prefixes_table_from_page(self) -> List[RowPrefixesTable]:
        try:
            div = self.headless_browser.driver.find_element(By.ID, 'pfx_table_div')
        except selenium.common.exceptions.NoSuchElementException:
            raise
        try:
            table = div.find_element(By.TAG_NAME, 'table')
        except selenium.common.exceptions.NoSuchElementException:
            raise
        try:
            tbody = table.find_element(By.TAG_NAME, "tbody")
        except selenium.common.exceptions.NoSuchElementException:
            raise
        try:
            trs = tbody.find_elements(By.TAG_NAME, "tr")
        except selenium.common.exceptions.NoSuchElementException:
            raise
        prefixes_table = list()
        for tr in trs:
            try:
                tds = tr.find_elements(By.TAG_NAME, 'td')
            except selenium.common.exceptions.NoSuchElementException:
                raise
            try:
                # tds[0].text is the index number
                tmp = RowPrefixesTable(tds[1].text, tds[2].text, tds[3].text, tds[4].text, tds[5].text, tds[6].text, tds[7].text)
                prefixes_table.append(tmp)
            except (ValueError, NotROVStateTypeError):
                raise
        return prefixes_table

    def get_network_if_present(self, ip: ipaddress.IPv4Address) -> RowPrefixesTable:
        try:
            div = self.headless_browser.driver.find_element(By.ID, 'pfx_table_div')
        except selenium.common.exceptions.NoSuchElementException:
            raise
        try:
            table = div.find_element(By.TAG_NAME, 'table')
        except selenium.common.exceptions.NoSuchElementException:
            raise
        try:
            tbody = table.find_element(By.TAG_NAME, "tbody")
        except selenium.common.exceptions.NoSuchElementException:
            raise
        try:
            trs = tbody.find_elements(By.TAG_NAME, "tr")
        except selenium.common.exceptions.NoSuchElementException:
            raise
        for tr in trs:
            try:
                tds = tr.find_elements(By.TAG_NAME, 'td')
            except selenium.common.exceptions.NoSuchElementException:
                raise
            try:
                network = ipaddress.ip_network(tds[2].text)
                if ip in network:
                    try:
                        # tds[0].text is the index number
                        return RowPrefixesTable(tds[1].text, tds[2].text, tds[3].text, tds[4].text, tds[5].text, tds[6].text, tds[7].text)
                    except (ValueError, NotROVStateTypeError):
                        raise
                else:
                    pass
            except ValueError:
                raise
        raise NetworkNotFoundError(ip.compressed)

    @staticmethod
    def base_url(as_number: int) -> str:
        return 'https://stats.labs.apnic.net/roa/AS'+str(as_number)+'?c=IT&l=1&v=4&t=thist&d=thisd'