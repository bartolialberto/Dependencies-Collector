
import re

from selenium.webdriver.firefox.options import Options
from seleniumwire import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import *



class ScriptOriginScraper:
    """
    This class set a driver which can look for scripts origin, given a url
    """
    def __init__(self, dPath='C:/Users/leona/Desktop/TesiMagistrale/PythonProject/MyPackages/geckodriver', fPath='C:/Program Files/Mozilla Firefox/firefox.exe', sleepTime = 30):
        """
        This constructor configures the driver data
        """
        self.driverPath = dPath
        self.firefoxPath = fPath
        self.driver = None
        self.options = Options()
        self.options.headless = True
        self.sleepTime = sleepTime


    def getScriptOrigin(self, url):
        """
        This method connect the driver to an url and scrape the script origins from src attribute, it found also if the scripts have integrity attribute or if it is in the default web page or is inside an iframe
        :param self: self object, which has info about driver configuration
        :param url: a string representing an url.
        :return: a list of tuple of three element, the first is the url from which the script is downloaded, the second is a boolean which is True if there is the integrity attribute, and the third is a boolean which is True if the script in the DOM is in an iframe
        """
        #look for not in line script and return a list of tuple (src, integrity, inFrame)
        binary = FirefoxBinary(self.firefoxPath)
        self.driver = webdriver.Firefox(executable_path=self.driverPath, options=self.options, firefox_binary=binary)
#        self.driver.implicitly_wait(self.sleepTime)
        print("Starting headless browser...")
        self.driver.get(url)
        print("Scraping scripts...")

        #iframeElement = self.driver.find_elements_by_xpath("//iframe")

  #      iframe1 = self.driver.find_elements_by_xpath("//iframe")
        #iframe2 = self.driver.find_elements_by_tag_name("iframe")

        #self.driver.switch_to.default_content()
        try:
            scriptElements = self.driver.find_elements_by_tag_name('script')
        except NoSuchElementException:
            print("No scripts at this URL: ", url)
            return None

        returnList = list()
        integrity = False
        inFrame = False
        for s in scriptElements:
            integrity = False
            inFrame = False

            source = s.get_attribute("src")
            if source == '':
                #mi interesso solo a script non inline
                continue

            attribute = s.get_attribute("integrity")
            if attribute != '':
                integrity = True

            parent = s
            while True:
                #print(parent.tag_name)
                try:
                    parent = parent.find_element_by_xpath('..')
                    if parent.tag_name == "iframe":
                        inFrame = True
                        returnList.append((source, integrity, inFrame))
                        break
                except WebDriverException as ex:
                    #print("Reached top of the DOM")
                    returnList.append((source, integrity, inFrame))
                    break
                except Exception as e:
                    print("Exception ,", e)
                    #returnList.append((source, integrity, inFrame))
                    break


            #print(parent.tag_name, "--->", s.tag_name)

        iframe2 = self.driver.find_elements_by_tag_name("iframe")
        self.driver.switch_to.default_content()
        for el in iframe2:
            try:
                self.driver.switch_to.frame(el)
            except Exception as e:
                print("Errore in switch to frame:", e)
                continue

            scriptElements = self.driver.find_elements_by_tag_name('script')
            for i in scriptElements:
                integrity = False
                #print(i.text)
                source = i.get_attribute("src")
                if source == '':
                    # mi interesso solo a script non inline
                    continue

                attribute = i.get_attribute("integrity")
                if attribute != '':
                    integrity = True

                returnList.append((source, integrity, True))

            self.driver.switch_to.default_content()

        self.close()

        return returnList


    def getScriptOriginsDomainsList(self, url):
        """
        This method get the web page at url in input and return the list of domain from which the scripts of the webpages are downloaded
        :param url: a string representing an url
        :return: a list of string, each representing a domain from which the scripts are downloaded
        """
        mat = re.findall("/", url)
        if len(mat) == 0:
            print("Error:",url ," is not a valid url")
            return None
        if len(mat) == 2:
            match = re.search("//(.*)", url)
            boundaries = match.span()
            domain = url[boundaries[0] + 2:boundaries[1]]
        else:
            match = re.search("//(.*?)/", url)
            boundaries = match.span()
            domain = url[boundaries[0] + 2:boundaries[1] - 1]
        print("Domain: ", domain)

        li = self.getScriptOrigin(url)
        finalList = list()
        tmp = None
        dm = None
        try:
            for el in li:
                tmp = el[0]
                scr = ""
                mat = re.findall("/", url)
                if len(mat) == 2:
                    match = re.search("//(.*)", tmp)
                    boundaries = match.span()
                    dm = tmp[boundaries[0] + 2:boundaries[1]]
                    scr = "/"
                else:
                    match = re.search("//(.*?)/", tmp)
                    boundaries = match.span()
                    dm = tmp[boundaries[0] + 2:boundaries[1] - 1]
                    scr = tmp[boundaries[1]:]
                    match2 = re.search("(.*?)\?", scr)
                    if match2 is not None:
                        bound = match2.span()
                        scr = scr[:bound[1]-1]

                if dm == domain:
                    li.remove(el)
                    continue
                finalList.append((dm, scr, el[1], el[2]))
        except Exception as e:
            print("Error: ", e)

        return finalList


    def close(self):
        """This method is called to close the driver"""
        self.driver.quit()
        return



#o = ScriptOriginScraper()
#li = o.getScriptOriginsDomainsList('https://clave-dninbrt.seg-social.gob.es/')#'https://www.google.com/')#'http://127.0.0.1:3000/page.html') #'https://www.challengermode.com/')
#print(li)
#with open("Buff.txt", "w") as csv_file:
#for e in li:
#    print(e)
#        csv_file.write(str(e))
