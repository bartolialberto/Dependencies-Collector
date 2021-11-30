import ipaddress
from typing import List
import selenium
from selenium.webdriver.common.by import By
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.ROVStates import ROVStates
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError


class RowPrefixesTable:
    """
    This class represent a row of the pfx_table_div (id of html element) table in the page (ROV page):
            https://stats.labs.apnic.net/roa/ASXXXX?c=IT&l=1&v=4&t=thist&d=thisd
    where XXXX is the autonomous system number.

    ...

    Attributes
    ----------
    as_number : `int`
        The autonomous system number.
    prefix : `ipaddress.IPv4Network`
        The row prefix announced from the current autonomous system.
    span : `int`
        The span.
    cc : `str`
        The cc.
    visibility : `int`
        The visibility.
    rov_state : `ROVStates`
        The ROV state (UNKNOWN, INVALID, VALID).
    roas : `str`
        The ROAS.
    """
    def __init__(self, as_number: str, prefix: str, span: str, cc: str, visibility: str, rov_state: str, roas: str):
        """
        Initialize an object from a string representation of every attribute.

        :param as_number:
        :type as_number: str
        :param prefix:
        :type as_number: str
        :param span:
        :type span: str
        :param cc:
        :type cc: str
        :param visibility:
        :type visibility: str
        :param rov_state:
        :type rov_state: str
        :param roas:
        :type roas: str
        :raise ValueError: If as_number is not a parsable integer number or it's an integer number < 0.
        :raise ValueError: If prefix is not a valid string representation of a IPv4Network.
        :raise ValueError: If span is not a parsable integer number.
        :raise ValueError: If cc is a string with length != 2.
        :raise ValueError: If visibility is not a parsable integer number.
        :raise NotROVStateTypeError: If rov_state is not a parsable ROV state.
        """
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
    """
    This class represent a scraper that looks for the pfx_table_div (id of html element) table in the page (ROV page):
            https://stats.labs.apnic.net/roa/ASXXXX?c=IT&l=1&v=4&t=thist&d=thisd
    where XXXX is the autonomous system number. Requires a valid headless browser to work associated to geckodriver.
    In particular geckodriver executable needs to be placed in the input folder of the project root folder (PRD).

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
        Self-explanatory.

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
        :raise selenium.common.exceptions.WebDriverException: If something goes wrong with the request.
        """
        try:
            self.headless_browser.driver.get(url_page)
        except selenium.common.exceptions.WebDriverException:
            raise
        self.prefixes_table.clear()
        self.current_as_number = -1

    def load_as_page(self, as_number: int) -> None:
        """
        Execute a GET of the url that is associated with the autonomous system number parameter. The result is in the
        state of the headless browser.

        :param as_number: The autonomous system number.
        :type as_number: int
        :raise ValueError: If the autonomous system number is < 0.
        :raise selenium.common.exceptions.WebDriverException: If something goes wrong with the request.
        :raise selenium.common.exceptions.NoSuchElementException: If there's a problem while parsing all the html
        elements to reach the pfx_table_div (id html element) table.
        :raise ValueError: If the data found for a row are not formatted as expected. See __init__() of class
        RowPrefixesTable.
        :raise TableEmptyError: If the pfx_table_div (id html element) table is empty.
        :raise NotROVStateTypeError: If the data found for a row are not formatted as expected. See __init__() of class
        RowPrefixesTable.
        """
        if as_number < 0:
            raise ValueError
        else:
            self.load_page(ROVPageScraper.base_url(as_number))
            self.prefixes_table.clear()
            self.current_as_number = as_number
            self.scrape_prefixes_table_from_page()

    def scrape_prefixes_table_from_page(self) -> List[RowPrefixesTable]:
        """
        This method scrape the current page in the headless browser to find the pfx_table_div (id html element) table
        constructed (normally) in the ROV page. Obviously it needs a previous load of a valid autonomous system page.
        See method: load_as_page().

        :raise selenium.common.exceptions.NoSuchElementException: If there's a problem while parsing all the html
        elements to reach the pfx_table_div (id html element) table.
        :raise ValueError: If the data found for a row are not formatted as expected. See __init__() of class
        RowPrefixesTable.
        :raise TableEmptyError: If the pfx_table_div (id html element) table is empty.
        :raise NotROVStateTypeError: If the data found for a row are not formatted as expected. See __init__() of class
        RowPrefixesTable.
        :return: A list of RowPrefixesTable objects to represent the pfx_table_div (id html element) table.
        :rtype: List[RowPrefixesTable]
        """
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
            raise TableEmptyError
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
        self.prefixes_table = prefixes_table
        return prefixes_table

    def get_network_if_present(self, ip: ipaddress.IPv4Address) -> RowPrefixesTable:
        """
        This method search in the table saved in the state of this ROVPageScraper object a row containing a prefix which
        contains the address parameter. In other words, before this method you have to invoke load_as_page(as_number)
        method.


        :param ip: An ip v4 address.
        :type ip: ipaddress.IPv4Address
        :raise TableEmptyError: If the pfx_table_div (id html element) table is empty.
        :raise NetworkNotFoundError: If a network that contains the ip parameter is not found in the table.
        :return: The matched row (from the prefix) in the table.
        :rtype: RowPrefixesTable
        """
        if len(self.prefixes_table) == 0:
            raise TableEmptyError(self.current_as_number)
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
