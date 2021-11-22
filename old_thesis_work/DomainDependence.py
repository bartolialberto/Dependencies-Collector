from Resolver import Resolver
from NetNumberResolver import NetNumberResolver
from LandingSite import LandingSite
from ROVScrape import ROVScraper
#from SoftwareDependencies import SoftwareDependencies
from ScriptOriginScrape import ScriptOriginScraper
import sqlite3
import ipaddress
import re

class DomainDependence:
    """
    This class is useful to find the dependencies a web domain depends on and save these dependencies on a database. The dependecies are: CNAME aliases, zones name, name servers name, name servers IP addresses, range of name servers IP addresses, autonomous systems and location of the autonomous systems.
    This class has two fields:
    - dataBase: a string representing the name of a sqlite database file, it is used to open the corresponding file and execute operations on the database.
    - domainsInformation: a list of dictionaries with the information found by the method multipleDomainsDependencies, to retrieve these informations the recommendation is to call the get methods described below.
    """
    dataBase = None
    domainsInformation = list()

    def __init__(self, dbname = "Results.sqlite"):
        """
        This constructor sets the dataBase field.
        :param dbname: is a string representing the name of a sqlite database file, if the user does not want to save the result in a database can put None as input. Default is None.
        """
        self.dataBase = dbname


#questo metodo sotto non richiama n volte il metodo sopra ma crea un oggetto Resolver solo e richiama n volte i suoi metodi, serve così perché sennò mi sovrascrivo la cache e i risultati, invece così trovo prima tuttti i risultati e poi proseguo
    def multipleDomainsDependencies(self, domains, csv=None, path_ip2asn='C:/Users/leona/Desktop/TesiMagistrale/IPv4ToASN/ip2asn-v4.tsv', path_geckodriver = '/Users/leona/Desktop/TesiMagistrale/PythonProject/MyPackages/geckodriver',path_firefox = 'C:/Program Files/Mozilla Firefox/firefox.exe'):
        """
        This method finds all the dependencies of a list of domains using other classes like: RRecord, Resolver, NetNumberResolver, OpenDataBase and LandingSite. It finds these dependencies: CNAME aliases, zones name, name servers name, name servers IP addresses, range of name servers IP addresses, autonomous systems and location of the autonomous systems. This method opens the database file with the name stored in field dataBase and saves for each domain in domains input its dependencies in different tables. This method saves the dependencies information also in the field domainsInformation, as a dictionary, to retrieve these informations the recommendation is to call the get methods described below. Moreover, this method creates two new files: NewCache.csv, Error.csv. The NewCache.csv file is a file which contains all the resource records found during the research for dependencies of the domains in input; it could be used as a cache file for a future execution of this method. The Error.csv file contains a list of domains, these domains are domains that this method can’t find dependencies of, due to some error, in the file is written what kind of error for each domain. If the dependencies for all the domains are found without errors the Error.csv file is not created.
        :param domains:  is a list of web domains as strings.
        :param csv: is the name of a cache file which contains resource records information, default value is None.
        :return: this method has no return values, instead it creates a NewCache.csv file, a Error.csv file, it add a new dictionary to the domainsInformation field, and save the dependencies found in a database with the name saved in the field dataBase.
        """
        objResolver = Resolver(csv)
        domIpCname = list()
        cnamedDomains = list()

        rangeValidate = list()
        #check if domain in domains are valid domain
        for dom in reversed(domains):
            check = re.findall("[/@,#]", dom)
            if len(check) != 0:
                print("WebDomain is not a valid domain: ", dom)
                objResolver.logError.append({"domain": dom, "error" : "Not a valid domain"})
                domains.remove(dom)

        for num1 in reversed(range(len(domains))):
            for num2 in range(num1):
                if domains[num1] == domains[num2]:
                    domains.remove(domains[num1])
                    break

        domainOriginal = list()
        listSoftDependencies = list()
        for dm in domains:
            domainOriginal.append(dm)

        for dom in domains:
            tmp = dom
            if dom.endswith("."):
                tmp = dom[:len(dom)-1]

            sfScraper = ScriptOriginScraper(dPath=path_geckodriver, fPath=path_firefox)
            lis = sfScraper.getScriptOriginsDomainsList("https://"+tmp+"/")
            #lis = SoftwareDependencies.filterDependencies("https://"+tmp+"/")
            listSoftDependencies.append((dom, lis))
            #Ho cancellato le seguenti righe, mi fermo solo al primo step di dipendenza sennò allunga troppo l'esecuzione
            #if lis is not None:
            #    for el in lis:
            #        if el not in domains:
            #            domains.append(el)

        for each in range(len(domains)):
            if not domains[each].endswith("."):
                domains[each] = domains[each] +"."

        conn = sqlite3.connect(self.dataBase)
        cur = conn.cursor()
        cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='hostInformation' ''')
        # check if already exists in database
        #cancella sta riga, se uno vuole cercare le dipendense più volte per completezza che faccia, piuttosto togli repliche se nella lista in input c'è sono più volte lo stesso
        #if cur.fetchone()[0] == 1:
        #    for dom in reversed(domains):
        #        cur.execute('SELECT host FROM hostInformation WHERE host = ?', (dom,))
        #        rows = cur.fetchall()
        #        if len(rows) != 0:
        #            domains.remove(dom)
        #            print("Domain and its dependencies are already stored in database. Domain: ", dom)
        cur.close()

        if len(domains) == 0:
            print("Domain in input are all alredy stored in database, non need to look for them again")
            exit(0)

        for dom in domains:
            domainInformationDictionary = dict()
            domainInformationDictionary["Domain"] = dom
            tmp = objResolver.findIPandCNAME(dom)
            objLanding = LandingSite(dom)
            if objLanding.httpSite is not None:
                domainInformationDictionary["HTTPLanding"] = (True, objLanding.httpSite, objLanding.hsts, objLanding.redirected)
            else:
                domainInformationDictionary["HTTPLanding"] = (False, "Not_Accessible_via_http", objLanding.hsts, objLanding.redirected)

            if objLanding.httpsSite is not None:
                domainInformationDictionary["HTTPSLanding"] = (True, objLanding.httpsSite)
            else:
                domainInformationDictionary["HTTPSLanding"] = (False, "Not_Accessible_via_https")

            if tmp["IPs"] is None:
                print(dom, " has not an IPv4 address, maybe it is not the name of a server.")
                continue
            cnamedDomains.append(tmp["IPs"].name)
            domainInformationDictionary["IP"] = list()
            tmpList = tmp["IPs"].values
            for ipadrs in tmpList:
                asinfo = NetNumberResolver.resolve(ipadrs, netNumberDatabase = path_ip2asn)
                domainInformationDictionary["IP"].append((ipadrs, asinfo))

            domainInformationDictionary["Cname"] = list()
            if tmp["CNAMEs"] is not None:
                for cnm in tmp["CNAMEs"]:
                    cnamedDomains.append(cnm.name)
                    domainInformationDictionary["Cname"].append(cnm.values[0])
                    #qui dovrei fare anche domains.append(cnm.values[0]) aggiungo il cname ma non farlo piuttosto dopo in for each in fai in cnamedDomain
            domIpCname.append((dom, tmp))
            self.domainsInformation.append(domainInformationDictionary)

        #con il seguenti for cerco se le info dns di domini e cnamed domain e li metto tutti insieme
        for el in self.domainsInformation:
            dnsInfoDict = objResolver.findDNSInfo(el["Domain"])
            for cnm in el["Cname"]:
                cnameInfoDict = objResolver.findDNSInfo(cnm)
                alreadyExists = False
                for dix in cnameInfoDict:
                    for dics in dnsInfoDict:
                        if dix["Zone"] == dics["Zone"]:
                            alreadyExists = True
                            break
                    if not alreadyExists:
                        dnsInfoDict.append(dix)
                    alreadyExists = False
            #faccio ricerca anche per landing site se sono diversi
            landhttp = el["HTTPLanding"]
            if el["Domain"] != landhttp[1] and landhttp[1] != "Not_Accessible_via_http":
                landingDnsInfoDict = objResolver.findDNSInfo(landhttp[1])
                alreadyExists = False
                for dix in landingDnsInfoDict:
                    for dics in dnsInfoDict:
                        if dix["Zone"] == dics["Zone"]:
                            alreadyExists = True
                            break
                    if not alreadyExists:
                        dnsInfoDict.append(dix)
                    alreadyExists = False

            landhttps = el["HTTPSLanding"]
            if el["Domain"] != landhttps[1] and landhttps[1] != "Not_Accessible_via_https":
                landingDnsInfoDict = objResolver.findDNSInfo(landhttps[1])
                alreadyExists = False
                for dix in landingDnsInfoDict:
                    for dics in dnsInfoDict:
                        if dix["Zone"] == dics["Zone"]:
                            alreadyExists = True
                            break
                    if not alreadyExists:
                        dnsInfoDict.append(dix)
                    alreadyExists = False

            el["ZonesDependence"] = dnsInfoDict
            for diz in el["ZonesDependence"]:
                diz["NStoRange"] = list()
                for nmsrv in diz["NameServers"]:
                    for val in nmsrv.values:
                        net = NetNumberResolver.resolve(val, netNumberDatabase = path_ip2asn)
                        diz["NStoRange"].append({"IP": val, "RangeData": net})

        if self.dataBase is not None:
            conn = sqlite3.connect(self.dataBase)
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS host2Ip (id INTEGER PRIMARY KEY, host TEXT, IPv4 TEXT, UNIQUE(host, IPv4))')
            cur.execute('CREATE TABLE IF NOT EXISTS domain2cname (id INTEGER PRIMARY KEY, domain TEXT, cname INTEGER, UNIQUE(domain, cname))')
            cur.execute('CREATE TABLE IF NOT EXISTS hostInformation (id INTEGER PRIMARY KEY, host TEXT, cname INTEGER, landing_protocol_http BOOLEAN, landing_site_http TEXT, landing_protocol_https BOOLEAN, landing_site_https TEXT, STS_present BOOLEAN, is_redirected BOOLEAN, UNIQUE(host))')
            cur.execute('CREATE TABLE IF NOT EXISTS host2directZone (id INTEGER PRIMARY KEY, host TEXT, direct_zone TEXT, UNIQUE(host, direct_zone))')
            cur.execute('CREATE TABLE IF NOT EXISTS zone2synctacticDependence (id INTEGER PRIMARY KEY, zone TEXT, synctactic_zone TEXT, UNIQUE(zone, synctactic_zone))')
            cur.execute('CREATE TABLE IF NOT EXISTS zone2nameserver (id INTEGER PRIMARY KEY, zone TEXT, cname INTEGER, nameserver TEXT, UNIQUE(zone, nameserver))')
            cur.execute('CREATE TABLE IF NOT EXISTS IP2Range (id INTEGER PRIMARY KEY, ip_address TEXT, range TEXT, UNIQUE(ip_address, range))')
            cur.execute('CREATE TABLE IF NOT EXISTS range2AS (id INTEGER PRIMARY KEY, IP_range TEXT, AS_code TEXT, location_code TEXT, AS_description TEXT, UNIQUE(IP_range, AS_code, location_code, AS_description))')
            #cur.execute('CREATE TABLE IF NOT EXISTS domain2Software_Dependencies (id INTEGER PRIMARY KEY, domain TEXT, software_dependence TEXT, UNIQUE(domain, software_dependence))')
            cur.execute(
                'CREATE TABLE IF NOT EXISTS domain2Software_Dependencies (id INTEGER PRIMARY KEY, domain TEXT, host_dependence TEXT, script_path TEXT, integrity_present BOOLEAN, different_iframe BOOLEAN, UNIQUE(domain, host_dependence, script_path, integrity_present, different_iframe))')
            for el in self.domainsInformation:
                listIP = el["IP"]
                for ips in listIP:
                    cur.execute('INSERT OR IGNORE INTO host2Ip (host, IPv4) VALUES (?, ?)', (el['Domain'], ips[0]))
                    for rang in ips[1]:
                        rag = rang.Ipv4Range
                        cur.execute('INSERT OR IGNORE INTO IP2Range (ip_address, range) VALUES (?, ?)', (ips[0], rag))
                        code = "AS"+rang.code
                        cur.execute('INSERT OR IGNORE INTO range2AS (IP_range, AS_code, location_code, AS_description) VALUES (?, ?, ?, ?)', (rag, code, rang.geocode, rang.ASName))

                listcname = el["Cname"]
                curName = el['Domain']
                listUsefulDomainOfThisElement  = list()
                listUsefulDomainOfThisElement.append(curName)
                if len(listcname) !=0:
                    theFirst = listcname[0]
                    lastRow = 0
                    for cnms in reversed(listcname):
                        cur.execute('SELECT domain FROM domain2cname WHERE domain = ?', (cnms,))
                        row = cur.fetchone()
                        if row is not None:
                            #non sicuro di questo, sarebbe da testare, mi pare di sì
                            lastRow = row[0]
                        else:
                            cur.execute('INSERT INTO domain2cname (domain, cname) VALUES (?, ?)', (cnms, lastRow))
                            lastRow = cur.lastrowid
                        curName = cnms
                        if cnms == theFirst:
                            httpTuple = el["HTTPLanding"]
                            httpsTuple = el["HTTPSLanding"]
                            cur.execute('INSERT OR IGNORE INTO hostInformation (host, cname, landing_protocol_http, landing_site_http, landing_protocol_https, landing_site_https, STS_present, is_redirected) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (el['Domain'], lastRow, httpTuple[0], httpTuple[1], httpsTuple[0], httpsTuple[1], httpTuple[2], httpTuple[3]))
                        listUsefulDomainOfThisElement.append(curName)
                else:
                    httpTuple = el["HTTPLanding"]
                    httpsTuple = el["HTTPSLanding"]
                    cur.execute('INSERT OR IGNORE INTO hostInformation (host, cname, landing_protocol_http, landing_site_http, landing_protocol_https, landing_site_https, STS_present, is_redirected) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (el['Domain'], 0, httpTuple[0], httpTuple[1], httpsTuple[0], httpsTuple[1], httpTuple[2], httpTuple[3]))
                #qua va aggiunta di landingsite su listUswfulDomainOfThisElement così poi scrive anche sue informazioni
                landhttp = el["HTTPLanding"]
                if el["Domain"] != landhttp[1] and landhttp[1] != "Not_Accessible_via_http":
                    listUsefulDomainOfThisElement.append(landhttp[1])
                landhttps = el["HTTPSLanding"]
                if el["Domain"] != landhttps[1] and landhttps[1] != "Not_Accessible_via_https":
                    if landhttps[1] not in listUsefulDomainOfThisElement:
                        listUsefulDomainOfThisElement.append(landhttps[1])
                #ECCO QUI CREDO SIA L'INGHIPPO tutt e le righe che seguono devi farle ma dentro un for per ogni elemento di lista listUsefulDomainOfThisElement, quindi non solo per dominio di partenza ma anche per i suoi cname
                #tipo sta riga sotta fa subdomain non di el["Domain"] ma di ogni elemento di listUsefulDomainOfThisElement per ognuno di eseei
                #tipo: for each in listUsefulDomainOfThisElement:
                nameservers = list()
                for each in listUsefulDomainOfThisElement:
                    subdoms = objResolver.subdomains(each, rootIncluded=True)
                    isFirst = True
                    directZone = each
                    zonesSyntacticDependence = list()
                    for sbdom in reversed(subdoms):
                        for zones in el["ZonesDependence"]:
                            if zones["Zone"] == sbdom:
                                if isFirst:
                                    directZone = zones["Zone"]
                                    zonesSyntacticDependence.append(zones["Zone"])
                                    isFirst = False
                                    break
                                else:
                                    zonesSyntacticDependence.append(zones["Zone"])
                                    break

                    #nameservers = list() va fuori dal for
                    cur.execute('INSERT OR IGNORE INTO host2directZone (host, direct_zone) VALUES (?, ?)', (each, directZone))
                    for dom in zonesSyntacticDependence:
                        cur.execute('INSERT OR IGNORE INTO zone2synctacticDependence (zone, synctactic_zone) VALUES (?, ?)', (directZone, dom))
                        for zones in el["ZonesDependence"]:
                            if dom == zones["Zone"]:
                                listcname = zones["CNAME"]
                                #qui devo anche verificare se zona ha cname e in caso aggiungerla o rilinkarla se c'è già
                                lastRow = 0
                                for cnms in reversed(listcname):
                                    cur.execute('SELECT domain FROM domain2cname WHERE domain = ?', (cnms,))
                                    row = cur.fetchone()
                                    if row is not None:
                                        # non sicuro di questo, sarebbe da testare, mi pare di sì
                                        lastRow = row[0]
                                    else:
                                        cur.execute('INSERT INTO domain2cname (domain, cname) VALUES (?, ?)',
                                                    (cnms, lastRow))
                                        lastRow = cur.lastrowid

                                for ns in zones["NameServers"]:
                                    cur.execute(
                                        'INSERT OR IGNORE INTO zone2nameserver (zone, cname,  nameserver) VALUES (?, ?, ?)',
                                        (dom, lastRow, ns.name))
                                    alreadyExists = False
                                    for nsr in nameservers:
                                        if nsr.name == ns.name:
                                            alreadyExists = True
                                            break
                                    if not alreadyExists:
                                        nameservers.append(ns)
                                break
                #Da ECCO QUI fino a qua
                #da qui itero su tutti i nameserver a cascata
                for namserv in nameservers:
                    listIP = namserv.values
                    for ips in listIP:
                        cur.execute('INSERT OR IGNORE INTO host2Ip (host, IPv4) VALUES (?, ?)', (namserv.name, ips))
                        for dic in el["ZonesDependence"]:
                            for dix in dic["NStoRange"]:
                                if dix["IP"] == ips:
                                    for rng in dix["RangeData"]:
                                        rang = rng.Ipv4Range
                                        cur.execute('INSERT OR IGNORE INTO IP2Range (ip_address, range) VALUES (?, ?)', (ips, rang))
                                        code = "AS" + rng.code
                                        cur.execute(
                                            'INSERT OR IGNORE INTO range2AS (IP_range, AS_code, location_code, AS_description) VALUES (?, ?, ?, ?)',
                                            (rang, code, rng.geocode, rng.ASName))
                                    break
                    subdoms = objResolver.subdomains(namserv.name, rootIncluded=True)
                    isFirst = True
                    directZone = namserv.name
                    zonesSyntacticDependence = list()
                    for sbdom in reversed(subdoms):
                        for zones in el["ZonesDependence"]:
                            if zones["Zone"] == sbdom:
                                if isFirst:
                                    directZone = zones["Zone"]
                                    zonesSyntacticDependence.append(zones["Zone"])
                                    isFirst = False
                                    break
                                else:
                                    zonesSyntacticDependence.append(zones["Zone"])
                                    break
                    isAlreadyInNameservers = False
                    cur.execute('INSERT OR IGNORE INTO host2directZone (host, direct_zone) VALUES (?, ?)',
                                (namserv.name, directZone))
                    for dom in zonesSyntacticDependence:
                        cur.execute('INSERT OR IGNORE INTO zone2synctacticDependence (zone, synctactic_zone) VALUES (?, ?)',
                                    (directZone, dom))
                        for zones in el["ZonesDependence"]:
                            if dom == zones["Zone"]:
                                #pure qui aggiungo per cname come prima
                                listcname = zones["CNAME"]
                                # qui devo anche verificare se zona ha cname e in caso aggiungerla o rilinkarla se c'è già
                                lastRow = 0
                                for cnms in reversed(listcname):
                                    cur.execute('SELECT domain FROM domain2cname WHERE domain = ?', (cnms,))
                                    row = cur.fetchone()
                                    if row is not None:
                                        # non sicuro di questo, sarebbe da testare, mi pare di sì
                                        lastRow = row[0]
                                    else:
                                        cur.execute('INSERT INTO domain2cname (domain, cname) VALUES (?, ?)',
                                                    (cnms, lastRow))
                                        lastRow = cur.lastrowid

                                for ns in zones["NameServers"]:
                                    cur.execute(
                                        'INSERT OR IGNORE INTO zone2nameserver (zone, cname, nameserver) VALUES (?, ?, ?)',
                                        (dom, lastRow, ns.name))
                                    for nase in nameservers:
                                        if nase.name == ns.name:
                                            isAlreadyInNameservers = True
                                            break
                                    if not isAlreadyInNameservers:
                                        nameservers.append(ns)
                                    isAlreadyInNameservers = False

            #add software dependence table
            for n in listSoftDependencies:
                if n[1] != None:
                    for dmn in n[1]:
                        cur.execute('INSERT OR IGNORE INTO domain2Software_Dependencies (domain, host_dependence, script_path, integrity_present, different_iframe) VALUES (?, ?, ?, ?, ?)', (n[0], dmn[0], dmn[1], dmn[2], dmn[3]))

            conn.commit()
            cur.close()

        objResolver.save("newCache.csv")
        if len(objResolver.logError):
            fhandler = open("Error.csv", "w")
            for err in objResolver.logError:
                line = err["domain"] + ","+ err["error"]
                fhandler.write(line + "\n")
            fhandler.close()



    def getIP(self, domain):
        """
        This method searches for domain in the field domainsInformation and returns the IP addresses of that domain as a list of strings. If the domain is not resolved yet by multipleDomainDependecies the information is not available in the domainsInformation field and this method returns None.
        :param domain: a domain as a string
        :return: this method returns a list of string which represent the list of IPv4 address of the domain in input. If the domain is not already resolved by the method multipleDomainDependencies this method returns None.
        """
        for el in self.domainsInformation:
            if el["Domain"] == domain:
                return el["IP"]
        print("Domain not resolved yet")
        return None

    def getCname(self, domain):
        """
        This method searches for domain in the field domainsInformation and returns the alias of this domain as a list of strings, if the domain has no aliases the returned list is empty. If the domain is not resolved yet by multipleDomainDependecies the information is not available in the domainsInformation field and this method returns None.
        :param domain: a domain as a string
        :return: this method returns a list of string which represent the list of aliases  of the domain in input. If the domain is not already resolved by the method multipleDomainDependencies this method returns None.
        """
        for el in self.domainsInformation:
            if el["Domain"] == domain:
                if len(el["Cname"]) == 0:
                    print("This domain has no Cname")
                return el["Cname"]
        print("Domain not resolved yet")
        return None

    def getZones(self, domain):
        """
        This method searches for domain in the field domainsInformation and returns a list of strings representing the names of the zones the domain depends on. If the domain is not resolved  yet by multipleDomainDependecies the information is not available in the domainsInformation field and this method returns None.
        :param domain: a domain as a string
        :return: this method returns a list of strings representing the names of the zones the domain depends on. If the domain is not already resolved by the method multipleDomainDependencies this method returns None.
        """
        zones = list()
        for el in self.domainsInformation:
            if el["Domain"] == domain:
                for zn in el["ZonesDependence"]:
                    zones.append(zn["Zone"])
                return zones
        print("Domain not resolved yet")
        return None

    def getNameservers(self, domain):
        """
        This method searches for domain in the field domainsInformation and returns the information about the zones the domain depends on and their name servers.
        :param domain: a domain as string
        :return: This method returns a list of dictionaries with two keys: the first one is “Zone” and its value is the name of a zone on which domain depends on, the second one is “Nameservers'' and its value is a list of dictionaries with two keys. The first key of these dictionaries is “Name” and its value is the name of a nameserver of the zone on which domain depends on, the second key is “IPs” and its value is a list of IP addresses of the nameserver, as strings. If the input domain is not resolved yet by multipleDomainDependecies the information is not available in the domainsInformation field and this method returns None.
        """
        dix = list()
        for el in self.domainsInformation:
            if el["Domain"] == domain:
                for zn in el["ZonesDependence"]:
                    lisns = dict()
                    lisns["IPs"] = list()
                    lisnsIP = list()
                    for ns in zn["NameServers"]:
                        lisns["Name"] = ns.name
                        for ip in ns.values:
                            lisnsIP.append(ip)
                        lisns["IPs"] = lisnsIP
                    dix.append({"Zone": zn["Zone"], "Nameservers": lisns, "NameserverIP": lisnsIP})
                return dix
        print("Domain not resolved yet")
        return None

    def getNameserversIPinformation(self, domain):
        """
        This method searches for domain in the field domainsInformation and returns the information about the zones the domain depends on, their name servers addresses and the information about IP range the nameservers IP addresses belong to.
        :param domain: a domain as a string.
        :return:  The method returns a list of dictionaries with two keys: the first one is “Zone” and its value is the name of a zone on which domain depends on, the second one is “Nameservers'' and its value is a list of dictionaries with two keys. The first key of these dictionaries is “Name” and its value is the name of a nameserver of the zone on which domain depends on, the second key is “IPs” and its value is a list of dictionaries with two keys. The first key of these dictionaries is “IP” and its value is one of the IP addresses of the name server, the second key is “RangeInfo” and its value is a list of objects of class NetNumberResolver which contain in their fields the information about the ranges of IP addresses the IP of the name server is in and also about the autonomous system which manage these ranges. If the input domain is not resolved yet by multipleDomainDependecies the information is not available in the domainsInformation field and this method returns None.
        """
        dix = list()
        for el in self.domainsInformation:
            if el["Domain"] == domain:
                for zn in el["ZonesDependence"]:
                    finalList = list()
                    for ns in zn["NameServers"]:
                        lisns = dict()
                        lisns["IPs"] = list()
                        lisns["Name"] = ns.name
                        for ip in ns.values:
                            lisnsIP = dict()
                            lisnsIP["RangeInfo"] = list()
                            lisnsIP["IP"] = ip
                            for ipNet in zn["NStoRange"]:
                                if ipNet["IP"] == ip:
                                    for netinfo in ipNet["RangeData"]:
                                        lisnsIP["RangeInfo"].append(netinfo)
                                    break
                            lisns["IPs"].append(lisnsIP)
                        finalList.append(lisns)
                    dix.append({"Zone": zn["Zone"], "Nameservers": finalList})
                return dix
        print("Domain not resolved yet")
        return None

    @staticmethod
    def rangeVerificated(autsys, ranges, dPath= '/Users/leona/Desktop/TesiMagistrale/PythonProject/MyPackages/geckodriver' , fPath= 'C:/Program Files/Mozilla Firefox/firefox.exe'):
        """
        This method look for a list of ranges of IPv4 addresses managed by an autonomous system and return True of False for each of them if the range of IPv4 addresses is verified or not.
        :param autsys: a string representing an autonomous system code, in the form of AS + a number which identify the autonomous system
        :param ranges: a list of strings each of them represents a range of IPv4 addresses in the network number notation
        :param dPath: is a string representing the file path to the driver geckodriver
        :param fPath: is a string representing the file path to the executable file of Firefox browser.
        :return: a list of tuple of two elements, the first is a string representing a range of IPv4 addresses, the second is a boolean, True if the range of IPv4 addresses are verified by the autonomous system which manage them, False otherwise.
        """
        scraper = ROVScraper(dbg=True, dPath= dPath, fPath = fPath)
        scraper.loadASPage(autsys[2:])
        scrapeResults = scraper.getResults()
        scraper.__del__()
        returnList = list()
        for rang in ranges:
            net = ipaddress.ip_network(rang, strict=False)
            notFound = True
            for each in scrapeResults:
                netToCompare = ipaddress.ip_network(each[2])
                if net.version != netToCompare.version:
                    continue

                if net.compare_networks(netToCompare) == 0:
                    if each[6] == "VLD":
                        returnList.append((rang, True))
                        notFound = False
                        break
                    else:
                        returnList.append((rang, False))
                        notFound = False
                        break
                else:
                    isIt = net.subnet_of(netToCompare)
                    if isIt:
                        returnList.append((rang, True))
                        notFound = False
                        break
            if notFound:
                returnList.append((rang, False))

        return returnList

    def lookForVerifiedRange(self, dPath= '/Users/leona/Desktop/TesiMagistrale/PythonProject/MyPackages/geckodriver' , fPath= 'C:/Program Files/Mozilla Firefox/firefox.exe'):
        """
        This method gets the row of the table range2AS from the database which the name is found in self.dataBase and look for each range in the rows if they are verified by the autonomous system which manage them.
        :param dPath: is a string representing the file path to the driver geckodriver
        :param fPath: is a string representing the file path to the executable file of Firefox browser.
        :return: this method has not return value but store the information about Ipv4 range and if them are verified in a table called range2verified in the database in self.dataBase
        """
        #potrei anche fare un ottimizzazzione magari prendere righe con stesso AS e raggrupparle
        conn = sqlite3.connect(self.dataBase)
        cur = conn.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS range2verificated (id INTEGER PRIMARY KEY, range TEXT, verificated BOOLEAN, UNIQUE(range, verificated))')
        cur.execute('SELECT IP_range, AS_code FROM range2AS')
        records = cur.fetchall()
        # ordino i records in modo che siano raggruppati per as
        switched = True
        while switched:
            switched = False
            for i in range(len(records)-1):
                print(records[i+1][1], records[i][1])
                if records[i+1][1] < records[i][1]:
                    tmp = records[i+1]
                    records[i+1] = records[i]
                    records[i] = tmp
                    switched = True

        for ele in records:
            print(ele)

        currentList = list()
        for i in range(len(records)-1):
            currentList.append(records[i][0])

            if i == (len(records) - 2):
                if records[i + 1][1] == records[i][1]:
                    currentList.append(records[i + 1][0])
                    verificated = self.rangeVerificated(records[i][1], currentList, dPath=dPath, fPath=fPath)
                    for tpl in verificated:
                        cur.execute('INSERT OR IGNORE INTO range2verificated (range, verificated) VALUES (?, ?)',
                                    (tpl[0], tpl[1]))
                    currentList = list()
                else:
                    tmpList = list()
                    tmpList.append(records[i+1][0])
                    verificated = self.rangeVerificated(records[i+1][1], tmpList, dPath=dPath, fPath=fPath)
                    for tpl in verificated:
                        cur.execute('INSERT OR IGNORE INTO range2verificated (range, verificated) VALUES (?, ?)',
                                    (tpl[0], tpl[1]))

            if records[i+1][1] != records[i][1]:
                verificated = self.rangeVerificated(records[i][1], currentList, dPath=dPath, fPath=fPath)
                for tpl in verificated:
                    cur.execute('INSERT OR IGNORE INTO range2verificated (range, verificated) VALUES (?, ?)',
                            (tpl[0], tpl[1]))
                currentList = list()

        conn.commit()
        cur.close()

    def lookForVerifiedRangePartial(self, rangeList, dPath= '/Users/leona/Desktop/TesiMagistrale/PythonProject/MyPackages/geckodriver' , fPath= 'C:/Program Files/Mozilla Firefox/firefox.exe'):
        """
        This method doesn't have attributes. It get the row of the table range2AS from the database which the name is found in self.dataBasa and look for each range in the rows if they are verified by the autonomous system which manage them.
        :return: this method has not return value but store the information about Ipv4 range and if them are verified in a table called range2verified in the database in self.dataBase
        """
        #potrei anche fare un ottimizzazzione magari prendere righe con stesso AS e raggrupparle
        conn = sqlite3.connect(self.dataBase)
        cur = conn.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS range2verificated (id INTEGER PRIMARY KEY, range TEXT, verificated BOOLEAN, UNIQUE(range, verificated))')
        cur.execute('SELECT IP_range, AS_code FROM range2AS')
        records = list()
        for rng in rangeList:
            cur.execute('SELECT IP_range, AS_code FROM range2AS where IP_range = \''+rng+'\'')
            rows = cur.fetchall()
            for r in rows:
                records.append(r)

        # ordino i records in modo che siano raggruppati per as
        switched = True
        while switched:
            switched = False
            for i in range(len(records)-1):
                print(records[i+1][1], records[i][1])
                if records[i+1][1] < records[i][1]:
                    tmp = records[i+1]
                    records[i+1] = records[i]
                    records[i] = tmp
                    switched = True

        for ele in records:
            print(ele)

        currentList = list()
        for i in range(len(records)-1):
            currentList.append(records[i][0])

            if i == (len(records) - 2):
                if records[i + 1][1] == records[i][1]:
                    currentList.append(records[i + 1][0])
                    verificated = self.rangeVerificated(records[i][1], currentList, dPath=dPath, fPath=fPath)
                    for tpl in verificated:
                        cur.execute('INSERT OR IGNORE INTO range2verificated (range, verificated) VALUES (?, ?)',
                                    (tpl[0], tpl[1]))
                    currentList = list()
                else:
                    tmpList = list()
                    tmpList.append(records[i+1][0])
                    verificated = self.rangeVerificated(records[i+1][1], tmpList, dPath=dPath, fPath=fPath)
                    for tpl in verificated:
                        cur.execute('INSERT OR IGNORE INTO range2verificated (range, verificated) VALUES (?, ?)',
                                    (tpl[0], tpl[1]))

            if records[i+1][1] != records[i][1]:
                verificated = self.rangeVerificated(records[i][1], currentList, dPath=dPath, fPath=fPath)
                for tpl in verificated:
                    cur.execute('INSERT OR IGNORE INTO range2verificated (range, verificated) VALUES (?, ?)',
                            (tpl[0], tpl[1]))
                currentList = list()

        conn.commit()
        cur.close()


# fhand = open("Buff.txt", 'r')
# lines = fhand.readlines()
# lista = list()
# for line in lines:
    #lista.append(line.strip())

# o = DomainDependence("TESTNNESIMO.sqlite")
# o.multipleDomainsDependencies(lista,
       # path_ip2asn='C:/Users/leona/Desktop/TesiMagistrale/IPv4ToASN/ip2asn-v4.tsv',
        # path_geckodriver = 'C:/Users/leona/Desktop/TesiMagistrale/PythonProject/MyPackages/geckodriver',
        # path_firefox = 'C:/Program Files/Mozilla Firefox/firefox.exe')
#o.lookForVerifiedRange()


#o.multipleDomainsDependencies(lista, csv="cCache.csv")