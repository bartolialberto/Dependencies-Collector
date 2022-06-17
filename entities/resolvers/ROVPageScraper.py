import ipaddress
from typing import List
import requests
import re
from entities.RowPrefixesTable import RowPrefixesTable
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError


class ROVPageScraper:
    def __init__(self, dbg=False):
        self.baseUrl = 'https://stats.labs.apnic.net/roa/AS'
        self.pageLoaded = False
        self.sleepTime = 30
        self.dbg = dbg
        self.prefixes_table = list()
        self.responseDocument = None
        self.extractorRegex = 'var roatable.*\(\[.*]\s*\]\);'

    def loadPage(self, urlPage):
        if self.dbg:
            print('Loading page ', urlPage, ' ...')
        self.responseDocument = requests.get(urlPage).text.replace("\n", " ")
        self.pageLoaded = True
        if self.dbg:
            print('Page loaded')

    def load_as_page(self, asn):
        self.loadPage(self.baseUrl + str(asn))
        # ab - added for compatibility with Fabbio
        try:
            self.scrape_prefixes_table_from_page(asn)
        except (TableNotPresentError, ValueError, TableEmptyError, NotROVStateTypeError):
            raise

    def __scrapeTable(self):
        # good XPath tutorial
        # https://www.swtestacademy.com/xpath-selenium/#selenium-webdriver-tutorials
        scrapedData = []

        tableToScrape = re.findall(self.extractorRegex, self.responseDocument)
        if len(tableToScrape) != 0:
            #len = tableToScrape[0].count(']') - 2
            str1 = tableToScrape[0]
            ## ">213.208.0.0/19</a>
            indexes = [_.start() for _ in re.finditer("p=", str1)]
            for i in indexes:
                end = str1.find('\\', i)
                scrapedData.append(str1[i + 2:end])
                
        return scrapedData

    def getResults(self, xpath=None):
        if self.pageLoaded == False:
            raise Exception('Page not loaded')
        results = self.__scrapeTable()
        return results

    def __del__(self):
        if self.dbg:
            print('Destructor executed (no action needed)')


    def scrape_prefixes_table_from_page(self, asn) -> List[RowPrefixesTable]:
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
            roa_data = self.__scrapeTable()
            roa_data_len = len(roa_data)
            if roa_data_len != 0:
                for i in range(roa_data_len):
                #     def __init__(self, as_number: str, prefix: str, span: str, cc: str, visibility: str, rov_state: str, roas: str):
                    tmp = RowPrefixesTable('AS'+str(asn), roa_data[i], '256', 'IT', '10', 'VLD', ' ')
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
