import requests
import re
import urllib3
import certifi


class LandingSite:
    """
    The aim of this class is to help find if a webDomain is accessible via HTTP or HTTPS and which is the web domain
    reached in the two cases if it is not the same from the first one. We call the reached web domain "landing site".
    This class has four fields:
    - httpSite: is a string which represents the landing site in the case the connection is made via HTTP protocol.
        If the webDomain in the constructor input is not accessible via HTTP this field is set to None.
    - httpsSite: is a string which represents the landing site in the case the connection is made via HTTPS protocol.
        If the webDomain in the constructor input is not accessible via HTTPS this field is set to None.
    - httpHistory: is a list of strings, each string is an URL and the list is the sequence of URLs the constructor
        follows due to the redirections made while it is trying to access the webDomain in input to the constructor
        itself via HTTP. If there is no redirection the list is empty.
    - httpsHistory: is a list of strings, each string is an URL and the list is the sequence of URLs the constructor
        follows due to the redirections made while it is trying to access the webDomain in input to the constructor
        itself via HTTPS. If there is no redirection the list is empty.
    """
    httpSite = None
    httpsSite = None
    httpHistory = list()
    httpsHistory = list()
    redirected = False
    hsts = False

    def __init__(self, webDomain):
        """
        This constructor initializes the class fields. This constructor tries to connect to the web host with webDomain
        name via HTTP and HTTPS and follows the redirections until it finds the web domain which actually returns a
        web page, we call this last web domain “landing site”.
        :param webDomain: is a string representing a web domain.
        """
        #look for landing site via http and https and the redirections
        #let's see if webDomain is the name of a domain
        self.httpHistory = list()
        self.httpsHistory = list()
        check = re.findall("[/@,#]", webDomain)
        if len(check) != 0:
            print("WebDomain is not a valid domain: ", webDomain)
            return

        if webDomain.endswith("."):
            webDomain = webDomain[:len(webDomain)-1]
        stsPresent = False
        isRedirected = False
        #try http
        try:
            r = requests.get("http://"+webDomain+"/")
            lastUrlWithHTTP = r.url
            for hist in r.history:
                self.httpHistory.append(hist.url)
                if hist.url.startswith("http:"):
                    lastUrlWithHTTP = hist.url

            if r.headers.get('strict-transport-security') is not None:
                stsPresent = True

            self.httpHistory.append(r.url)
            if lastUrlWithHTTP.startswith("http:"):
                mat = re.findall("/", lastUrlWithHTTP)
                if len(mat) == 2:
                    match = re.search("//(.*?)", lastUrlWithHTTP)
                    boundaries = match.span()
                    landing = lastUrlWithHTTP[boundaries[0] + 2:boundaries[1]]
                else:
                    match = re.search("//(.*?)/", lastUrlWithHTTP)
                    boundaries = match.span()
                    landing = lastUrlWithHTTP[boundaries[0]+2:boundaries[1]-1]
                self.httpSite = landing

            #questo if qui sotto potrebbe non servire dato che poi cerco comunque sito via https
            if r.url.startswith("https:"):
                mat = re.findall("/", r.url)
                if len(mat) == 2:
                    match = re.search("//(.*?)", r.url)
                    boundaries = match.span()
                    landing = r.url[boundaries[0] + 2:boundaries[1]]
                else:
                    match = re.search("//(.*?)/", r.url)
                    boundaries = match.span()
                    landing = r.url[boundaries[0]+2:boundaries[1]-1]
                self.httpsSite = landing
                isRedirected = True
        except Exception as e:
            print(webDomain, " not accessible with requests, try with urllib3", e)
            try:
                http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(), timeout=5.0)
                r = http.request('GET', "http://"+webDomain+"/")
                head = r.getheader('strict-transport-security')
                if head is not None:
                    stsPresent = True
                lastUrlWithHTTP = "http://"+webDomain+"/"
                landedOn = None
                for hist in range(len(r.retries.history)):
                    self.httpHistory.append(r.retries.history[hist].name)
                    if r.retries.history[hist].name.startswith("http:"):
                        lastUrlWithHTTP = r.retries.history[hist].name

                    if hist == len(r.retries.history)-1:
                        self.httpHistory.append(r.retries.history[hist].redirect_location)
                        if r.retries.history[hist].redirect_location.startswith("http:"):
                            lastUrlWithHTTP = r.retries.history[hist].redirect_location
                        elif r.retries.history[hist].redirect_location.startswith("https:"):
                            isRedirected = True

                if lastUrlWithHTTP.startswith("http:"):
                    mat = re.findall("/", lastUrlWithHTTP)
                    if len(mat) == 2:
                        match = re.search("//(.*?)", lastUrlWithHTTP)
                        boundaries = match.span()
                        landing = lastUrlWithHTTP[boundaries[0] + 2:boundaries[1]]
                    else:
                        match = re.search("//(.*?)/", lastUrlWithHTTP)
                        boundaries = match.span()
                        landing = lastUrlWithHTTP[boundaries[0] + 2:boundaries[1] - 1]
                    self.httpSite = landing
            except urllib3.exceptions.MaxRetryError:
                http = urllib3.PoolManager(cert_reqs='CERT_NONE', timeout=5.0)
                try:
                    r = http.request('GET', "http://"+webDomain+"/")
                    head = r.getheader('strict-transport-security')
                    if head is not None:
                        stsPresent = True
                    lastUrlWithHTTP = "http://" + webDomain + "/"
                    for hist in range(len(r.retries.history)):
                        self.httpHistory.append(r.retries.history[hist].name)
                        if r.retries.history[hist].name.startswith("http:"):
                            lastUrlWithHTTP = r.retries.history[hist].name

                        if hist == len(r.retries.history) - 1:
                            self.httpHistory.append(r.retries.history[hist].redirect_location)
                            if r.retries.history[hist].redirect_location.startswith("http:"):
                                lastUrlWithHTTP = r.retries.history[hist].redirect_location
                            elif r.retries.history[hist].redirect_location.startswith("https:"):
                                isRedirected = True

                    if lastUrlWithHTTP.startswith("http:"):
                        mat = re.findall("/", lastUrlWithHTTP)
                        if len(mat) == 2:
                            match = re.search("//(.*?)", lastUrlWithHTTP)
                            boundaries = match.span()
                            landing = lastUrlWithHTTP[boundaries[0] + 2:boundaries[1]]
                        else:
                            match = re.search("//(.*?)/", lastUrlWithHTTP)
                            boundaries = match.span()
                            landing = lastUrlWithHTTP[boundaries[0] + 2:boundaries[1] - 1]
                        self.httpSite = landing
                except Exception as e:
                    print(webDomain, " not find http landing site neither with requests nor with urllib3. Exception:", e)
            except Exception as e:
                print(webDomain, " not find http landing site neither with requests nor with urllib3. Exception:", e)

        # try https
        try:
            r = requests.get("https://" + webDomain + "/")
            lastUrlWithHTTPS = r.url
            for hist in r.history:
                self.httpsHistory.append(hist.url)
                if hist.url.startswith("https:"):
                    lastUrlWithHTTPS = hist.url

            self.httpsHistory.append(r.url)
            if r.url.startswith("https:"):
                mat = re.findall("/", r.url)
                if len(mat) == 2:
                    match = re.search("//(.*?)", r.url)
                    boundaries = match.span()
                    landing = r.url[boundaries[0] + 2:boundaries[1]]
                else:
                    match = re.search("//(.*?)/", r.url)
                    boundaries = match.span()
                    landing = r.url[boundaries[0]+2:boundaries[1]-1]
                self.httpsSite = landing
        except Exception as e:
            print(webDomain, " not accessible with requests, try with urllib3", e)
            try:
                http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(), timeout=5.0)
                r = http.request('GET', "https://" + webDomain + "/")
                lastUrlWithHTTP = "https://" + webDomain + "/"
                for hist in r.retries.history:
                    self.httpsHistory.append(hist.name)
                    if hist.name.startswith("https:"):
                        lastUrlWithHTTP = hist.redirect_location

                if lastUrlWithHTTP.startswith("https:"):
                    mat = re.findall("/", lastUrlWithHTTP)
                    if len(mat) == 2:
                        match = re.search("//(.*?)", lastUrlWithHTTP)
                        boundaries = match.span()
                        landing = lastUrlWithHTTP[boundaries[0] + 2:boundaries[1]]
                    else:
                        match = re.search("//(.*?)/", lastUrlWithHTTP)
                        boundaries = match.span()
                        landing = lastUrlWithHTTP[boundaries[0] + 2:boundaries[1] - 1]
                    self.httpsSite = landing
            except urllib3.exceptions.MaxRetryError:
                http = urllib3.PoolManager(cert_reqs='CERT_NONE', timeout=5.0)
                try:
                    r = http.request('GET', "https://" + webDomain + "/")
                    lastUrlWithHTTP = "https://" + webDomain + "/"
                    for hist in r.retries.history:
                        self.httpsHistory.append(hist.name)
                        if hist.name.startswith("https:"):
                            lastUrlWithHTTP = hist.redirect_location
                    if lastUrlWithHTTP.startswith("https:"):
                        mat = re.findall("/", lastUrlWithHTTP)
                        if len(mat) == 2:
                            match = re.search("//(.*?)", lastUrlWithHTTP)
                            boundaries = match.span()
                            landing = lastUrlWithHTTP[boundaries[0] + 2:boundaries[1]]
                        else:
                            match = re.search("//(.*?)/", lastUrlWithHTTP)
                            boundaries = match.span()
                            landing = lastUrlWithHTTP[boundaries[0] + 2:boundaries[1] - 1]
                        self.httpsSite = landing
                except Exception as e:
                    print(webDomain, " not find https landing site neither with requests nor with urllib3. Exception:",
                          e)
            except Exception as e:
                print(webDomain, " not find https landing site neither with requests nor with urllib3. Exception:", e)

        finally:
            if self.httpSite != None:
                if not self.httpSite.endswith("."):
                    self.httpSite = self.httpSite + "."

            if self.httpsSite != None:
                if not self.httpsSite.endswith("."):
                    self.httpsSite = self.httpsSite + "."

            self.hsts = stsPresent
            self.redirected = isRedirected



#fhand = open("Buff.txt", 'r')
#lines = fhand.readlines()
#lista = list()
#for line in lines:
#    lista.append(line.strip())

#for l in lista:
#    o = LandingSite(l)
#    print(o.httpSite, o.httpsSite, o.httpHistory, o.httpsHistory, o.hsts, o.redirected)