from selenium.webdriver.firefox.options import Options
from seleniumwire import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import re


class SoftwareDependencies:

    @staticmethod
    def findDependencies(url, fPath = 'C:/Program Files/Mozilla Firefox/firefox.exe', dPath= "/Users/leona/Desktop/TesiMagistrale/PythonProject/MyPackages/geckodriver"):
        """
        A static method which given a url finds all the domains the web page of the url depends on, because script
        source depends on it
        :param url: a string representing a valid URL
        :return: a list of domain which are domain of the script source at URL page
        """
        options = Options()
        options.headless = True

        binary = FirefoxBinary(fPath)
        driver = webdriver.Firefox(executable_path = dPath,options=options, firefox_binary=binary)

        # Go to the url home page
        try:
            driver.get(url)
        except Exception as e:
            print(url, ": ", e)
            return None

        domainList = list()
        # Access requests via the `requests` attribute
        print("Dependencies found:")
        print(" URL  |   response_code   |   content-Type")
        for request in driver.requests:
            if request.response:
                if request.response.headers["Content-Type"] != None:
                    if "javascript" in request.response.headers['Content-Type'] or "application/" in request.response.headers['Content-Type']:
                        print(
                            request.url, "  |   " ,
                            request.response.status_code, " |   ",
                            request.response.headers['Content-Type']
                        )
                        domain = request.host
                        if domain not in domainList:
                            domainList.append(domain)
        driver.quit()
        return domainList

    @staticmethod
    def filterDependencies(url, fPath='C:/Program Files/Mozilla Firefox/firefox.exe', dPath= "/Users/leona/Desktop/TesiMagistrale/PythonProject/MyPackages/geckodriver"):
        """
        A static method which get an url of a webpage as attribute and finds all the web domain the wabpage depdens on
        excluding the web domain of the url itself.
        :param url: a string representing an URL
        :return: a list of web domain, these are domain the web page in input depends on.
        """
        mat = re.findall("/", url)
        if len(mat) == 2:
            match = re.search("//(.*)", url)
            boundaries = match.span()
            domain = url[boundaries[0] + 2:boundaries[1]]
        else:
            match = re.search("//(.*?)/", url)
            boundaries = match.span()
            domain = url[boundaries[0] + 2:boundaries[1] -1]
        print("Looking for software dependencies of domain: ", domain)
        li = SoftwareDependencies.findDependencies(url, fPath = fPath, dPath= dPath)
        try:
            for el in li:
                if el == domain:
                    li.remove(el)
        except Exception as e:
            print("Error: ", e)

        return li


#o = SoftwareDependencies.filterDependencies('https://www.google.com/')
#o = SoftwareDependencies.filterDependencies("https://pasarela.clave.gob.es/")
#print("List of domains: ", o)