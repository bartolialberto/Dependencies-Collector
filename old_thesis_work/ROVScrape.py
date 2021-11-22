import time
# install Firefox and geckodriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class ROVScraper:

    def __init__(self, dbg, dPath='/Users/Alberto/Downloads/geckodriver', fPath='C:/Program Files/Mozilla Firefox/firefox.exe'):
        self.baseUrl = 'https://stats.labs.apnic.net/roa/AS'
        self.driverPath = dPath
        self.firefoxPath = fPath
        self.driver = None
        self.options = Options()
        self.options.headless = True
        self.pageLoaded = False
        self.sleepTime = 30
        self.dbg = dbg
#       ab - This worked in April 2021
        self.xpathFirstRow = '//*[@id="pfx_table_div"]/div/div/table/tbody/tr'

    def createBrowser(self):
        binary = FirefoxBinary(self.firefoxPath)
        self.driver = webdriver.Firefox(executable_path=self.driverPath, options=self.options, firefox_binary=binary)
        if self.dbg:
            print('Headless browser created')

    def loadPage(self, urlPage):
        if self.driver == None:
            self.createBrowser()
        if self.dbg:
            print('Loading page ', urlPage, ' ...')
        self.driver.get(urlPage)
        self.pageLoaded = True
        if self.dbg:
            print('Page loaded')
        self.__waitForScripts()

    def loadASPage(self, asn):
        self.loadPage(self.baseUrl+str(asn))

    def __waitForScripts(self, sleepTime=None):
        # execute script to scroll down the page
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if self.dbg:
            print('Script being executed, sleeping...')
        if sleepTime == None:
            sleepTime = self.sleepTime
        time.sleep(sleepTime)
        if self.dbg:
            print('Awakened!')

    def __scrapeTable(self, xpathFirstRow):
        # how to scrape tables with Selenium
        # https://www.geeksforgeeks.org/scrape-table-from-website-using-python-selenium/
        # good XPath tutorial
        # https://www.swtestacademy.com/xpath-selenium/#selenium-webdriver-tutorials
        rows = self.driver.find_elements_by_xpath(xpathFirstRow)
        howManyRows = len(rows)
        howManyColumns = len(self.driver.find_elements_by_xpath(xpathFirstRow+'[1]/td'))

        scrapedData = []
        currXpath = self.xpathFirstRow
        for r in range(1, howManyRows+1):
            currRow = []
            for c in range(1, howManyColumns+1):
                currXpath = self.xpathFirstRow+'['+str(r)+']'+'/td['+str(c)+']'
                cellValue=self.driver.find_elements_by_xpath(currXpath)
                if cellValue[0].text == None:
                    currRow.append('')
                else:
                    currRow.append(cellValue[0].text)
            scrapedData.append(currRow)
        return scrapedData

    def getResults(self, xpath=None):
        if self.pageLoaded == False:
            raise Exception('Page not loaded')
        if xpath == None:
            xpath = self.xpathFirstRow
        results = self.__scrapeTable(xpath)
        return results

    def __del__(self):
        self.driver.quit()
        if self.dbg:
            print('Destructor executed')