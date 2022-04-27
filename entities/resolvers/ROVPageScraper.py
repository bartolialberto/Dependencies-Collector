import ipaddress
from typing import List
import selenium
from selenium.webdriver.common.by import By
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.RowPrefixesTable import RowPrefixesTable
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError


class ROVPageScraper:
    """
    This class represents a scraper that looks for the 'pfx_table_div' (id of html element) table in the page (ROV page):
            https://stats.labs.apnic.net/roa/ASXXXX?c=IT&l=1&v=4&t=thist&d=thisd
    where XXXX is the autonomous system number. Requires a valid headless browser to work associated to geckodriver.
    In particular geckodriver executable needs to be placed in the 'input' folder of the project root folder (PRD).

    ...

    Attributes
    ----------
    headless_browser : FirefoxHeadlessWebDriver
        An instance of a headless browser, in particular Firefox.
    prefixes_table : List[RowPrefixesTable]
        A list that represents the pfx_table_div (id of html element) table in the page (ROV page) saved state of this
        object to save computational time when asked to see if an ip address is contained in one of the prefixes in
        such table. We wanna avoid traversing the DOM for each address query.
    current_as_number : int
        An integer that saves the current as page loaded.
    """

    def __init__(self, headless_browser: FirefoxHeadlessWebDriver):
        """
        Initialize the object.

        :param headless_browser: The instance of a Firefox headless browser.
        :type headless_browser: FirefoxHeadlessWebDriver
        """
        self.headless_browser = headless_browser
        self.prefixes_table = list()
        self.current_as_number = -1

    def load_page(self, url_page: str) -> None:
        """
        Execute a GET of the url in the headless browser. The result is in the state of the headless browser.

        :param url_page: The url.
        :type url_page: str
        :raise selenium.common.exceptions.TimeoutException: If something goes wrong with the request and the timer is
        triggered.
        :raise selenium.common.exceptions.WebDriverException: If something goes wrong with the request.
        """
        try:
            self.headless_browser.driver.get(url_page)
        except selenium.common.exceptions.TimeoutException:
            self.headless_browser.close_and_reopen()
            self.prefixes_table = list()
            self.current_as_number = -1
            raise
        except selenium.common.exceptions.WebDriverException:
            self.prefixes_table = list()
            self.current_as_number = -1
            raise

    def load_as_page(self, as_number: int) -> None:
        """
        Execute a GET of the url that is associated with the autonomous system number parameter. The result is in the
        state of the headless browser.

        :param as_number: The autonomous system number.
        :type as_number: int
        :raise ValueError: If the autonomous system number is < 0.
        :raise selenium.common.exceptions.WebDriverException: If something goes wrong with the request.
        :raise TableNotPresentError: If there's a problem while parsing the html page.
        elements to reach the pfx_table_div (id html element) table.
        :raise ValueError: If the data found for a row are not formatted as expected. See __init__() of class
        RowPrefixesTable.
        :raise TableEmptyError: If there's a problem while parsing the html page.
        :raise NotROVStateTypeError: If the data found for a row are not formatted as expected. See __init__() of class
        RowPrefixesTable.
        """
        if as_number < 0:
            raise ValueError
        else:
            try:
                self.load_page(ROVPageScraper.base_url(as_number))
            except (selenium.common.exceptions.WebDriverException, selenium.common.exceptions.TimeoutException):
                raise
            self.current_as_number = as_number
            try:
                self.scrape_prefixes_table_from_page()
            except (TableNotPresentError, ValueError, TableEmptyError, NotROVStateTypeError):
                raise

    def scrape_prefixes_table_from_page(self) -> List[RowPrefixesTable]:
        """
        This method scrape the current page in the headless browser to find the pfx_table_div (id html element) table
        constructed (normally) in the ROV page. Obviously it needs a previous load of a valid autonomous system page.
        See method: load_as_page().

        :raise TableNotPresentError: If the pfx_table_div (id html element) or the table (html element) or the tbody
        (html element) are not found.
        :raise ValueError: If the data found for a row are not formatted as expected. See __init__() of class
        RowPrefixesTable.
        :raise TableEmptyError: If the aren't rows in the table.
        :raise NotROVStateTypeError: If the data found for a row are not formatted as expected. See __init__() of class
        RowPrefixesTable.
        :return: A list of RowPrefixesTable objects to represent the pfx_table_div (id html element) table.
        :rtype: List[RowPrefixesTable]
        """
        try:
            div = self.headless_browser.driver.find_element(By.ID, 'pfx_table_div')
        except selenium.common.exceptions.NoSuchElementException:
            self.prefixes_table = None
            raise TableNotPresentError(self.current_as_number)
        try:
            table = div.find_element(By.TAG_NAME, 'table')
        except selenium.common.exceptions.NoSuchElementException:
            self.prefixes_table = None
            raise TableNotPresentError(self.current_as_number)
        try:
            tbody = table.find_element(By.TAG_NAME, "tbody")
        except selenium.common.exceptions.NoSuchElementException:
            self.prefixes_table = None
            raise TableNotPresentError(self.current_as_number)
        try:
            trs = tbody.find_elements(By.TAG_NAME, "tr")
        except selenium.common.exceptions.NoSuchElementException:
            self.prefixes_table = list()
            raise TableEmptyError(self.current_as_number)
        self.prefixes_table = list()
        for tr in trs:
            try:
                tds = tr.find_elements(By.TAG_NAME, 'td')
            except selenium.common.exceptions.NoSuchElementException:
                self.prefixes_table = list()
                raise TableEmptyError(self.current_as_number)
            try:
                # tds[0].text is the index number
                tmp = RowPrefixesTable(tds[1].text, tds[2].text, tds[3].text, tds[4].text, tds[5].text, tds[6].text, tds[7].text)
                self.prefixes_table.append(tmp)
            except (ValueError, NotROVStateTypeError):
                self.prefixes_table = None
                raise
        return self.prefixes_table

    def get_network_if_present(self, ip: ipaddress.IPv4Address) -> RowPrefixesTable:
        """
        This method search in the table saved in the state of this ROVPageScraper object a row containing a prefix which
        contains the address parameter. In other words, before this method you have to invoke load_as_page(as_number)
        method.


        :param ip: An ip v4 address.
        :type ip: ipaddress.IPv4Address
        :raise TableEmptyError: If the pfx_table_div (id html element) table is empty.
        :raise TableNotPresentError: If the table (html element) is not present.
        :raise NetworkNotFoundError: If a network that contains the ip parameter is not found in the table.
        :return: The matched row (from the prefix) in the table.
        :rtype: RowPrefixesTable
        """
        if self.prefixes_table is None:
            raise TableNotPresentError(self.current_as_number)
        if len(self.prefixes_table) == 0:
            raise TableEmptyError(self.current_as_number, ip)
        for row in self.prefixes_table:
            if ip in row.prefix:
                return row
        raise NetworkNotFoundError(ip.compressed)

    @staticmethod
    def base_url(as_number: int) -> str:
        """
        Construct the base ROV page url from an autonomous system number.

        :param as_number: An integer that represents an autonomous system number.
        :type as_number: int
        :return: The ROV page url of that autonomous system number.
        :rtype: str
        """
        return 'https://stats.labs.apnic.net/roa/AS'+str(as_number)+'?c=IT&l=1&v=4&t=thist&d=thisd'
