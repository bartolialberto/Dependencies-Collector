# coding=utf-8
import dns.resolver
import re
from old_thesis_work.Zones import findRRecord, RRecord


class Resolver:
    """
    This class has a group of useful static method to find dns dependencies.
    This class has 2 fields:
    - cache: is a list of RRecord objects. It is initialized from the csv file passed as input to the constructor. It is useful to lighten the number of dns query made by the methods of this same class. If no .csv file is put as input for the constructor or such file is not found then the cache field is set to None.
    - logError: is a list of dictionaries which save information about errors found by the methods of this class while they are trying to find information about dns domains. The dictionaries have two keys. The first key is “Domain” which is a string representing a domain, this is a domain which causes some kind of error during the execution of some methods of this class. The second key is “Description” and its value is a string which is a description of the error occurred while a method was finding information about the domain in the “Domain” key.
    """
    cache = list()
    logError = list()

    def __init__(self, csv=None):
        """
        This class has some useful methods to find dns information. This constructor calls the load method.
        :param csv: csv is the name of a .csv file containing a list of resource records which will be used as a local cache. If no .csv file is passed as input the execution proceeds without cache. If the file is not found the execution stops and an error is printed on screen.
        """
        if csv is None:
            self.cache = list()
            return
        try:
            self.load(csv)
        except IOError:
            print("Cache file passed as input is not found. File name: ", csv)
            exit(1)
            return

    def findIPandCNAME(self, domain):
        """
        A method which takes a string representing a domain as input. This method makes a dns query of type A to find IPv4 addresses if domain is a name of a host. This method also finds CNAME records if domain is the name of a host with aliases.
        :param domain: a string representing a domain.
        :return: a dictionary with two keys. The first key is “IPs” and its value is an object of RRecord class with type “A” and values a list of IPv4 addresses, if there is no IP address or an exception is thrown the value is the string “NotAHost”. The second key is “CNAMEs” and its value is a list of objects of  RRecord class with type “CNAME” and domain as name, the values field is the alias. The value for the “CNAMEs” key is a list because this method finds all the aliases of domain, following a chain of CNAME until it reaches the domain which has a record of type A in dns. If there are no CNAME records with domain as name or an exception is thrown while dns resolves the CNAME query then the value is None.
        """
        res = dns.resolver.Resolver()
        res.nameservers = ["1.1.1.1"]
        if not domain.endswith("."):
            domain = domain + "."
        print("Searching for Ip addresses...")
        CNAMEDomains = list()
        currentName = domain
        resultA = None
        cached = True
        while True:
            check = self.cacheLookUp(currentName, "CNAME")  # ritorna il primo risultato (RRecord) nella cache, sennò None
            if check is not None:
                if check.values != "NXDomain" and check.values != "NoAnswer":
                    CNAMEDomains.append(check)
                    currentName = check.values[0]
                else:
                    if check.values == "NXDomain":
                        self.logError.append({"domain": currentName, "error": "this domain does not exists: NXDomain"})
                        print("NXDomain")
                        break
                    else:
                        #se arrivo qui vuol dire che la catena di CNAME sfocia nel nulla, o meglio che non ci sono  cname, no answer
                        print("This CNAME has not alias")
                        break
                check = self.cacheLookUp(currentName, "A")
                if check is not None:
                    if check.values != "NXDomain" and check.values != "NoAnswer":
                        resultA = check
                        break
                    else:
                        resultA = "NotAHost"
                        break
                else:
                    cached = False
                    break

        if not cached:
            result = findRRecord(currentName, "A")
            resultA = None
            if result is None:
                print("error in find RRecord:")
                #qui dovrei tornare errore in qualche modo, far sapere che sto dominio torna errore
                self.logError.append({"domain": currentName, "error": "Not found with dns.resolver"})
            else:
                resultA = result["Result"]
                if resultA is None:
                    print("some error in findRRecord")
                elif resultA.values == "NoAnswer" or resultA.values == "NXDomain":
                    self.cache.append(resultA)
                    resultA = "NotAHost"
                else:
                    if result["CNAME"] is not None:
                        for rr in result["CNAME"]:
                            found = self.cacheLookUp(rr.url, "CNAME")
                            if found is None:
                                self.cache.append(rr)
                            CNAMEDomains.append(rr)

        if len(CNAMEDomains) == 0:
            CNAMEDomains = None
        #ricorda che ips può tornare None se e solo se c'è stato errore nel findRRecord
        dictionary = {
            "IPs": resultA,
            "CNAMEs": CNAMEDomains
        }
        print(dictionary)
        return dictionary

    def findDNSInfo(self, domain):
        """
        This is a method which looks for the name of all the dns zones which domain depends on. If a domain and its subdomains are zone names we say that that domain depends on those zones, if the nameservers name of those zones belongs to another domain and its subdomains are zone names the domain depends also on those zones and so on with the name server names of those zones.
        :param domain:  is a string representing a domain in a fully qualified domain name. If the domain does not end with a dot the dot is added to make the domain in the fully qualified domain name notation. If domain is not a domain because it includes some special char, then the method prints an error on screen, returns None and set a dictionary with this error in the field logError.
        :return: a list of dictionaries with three keys.The first key is “Zone” and its value is a string which represents the name of the zone. The second key is “NameServers” and its value is a list of objects of class RRecord which is the list of resource records in the form: nameserver A IP-nameservers. This list contains all the resource records of this kind for the name servers of the zone which is the value of the key “Zone” of the dictionary. There is a dictionary for all the zones domain depends on. The third key is “CNAME” and its value is a list of RRecords which are resource records of type CNAME which are found while resolving the zone name, in the common case this list is empty.
        """
        check = re.findall("[/@,#]", domain)
        if len(check) != 0:
            print("WebDomain is not a valid domain: ", domain)
            self.logError.append({"domain": domain, "error": "Not a valid domain"})

        res = dns.resolver.Resolver()
        res.nameservers = ["1.1.1.1"]
        #if domain contains caratteri strani return None e setta valore in logErrror o meglio basta verificare che subdomains non sia NOn
        subdomains = Resolver.subdomains(domain, rootIncluded=True)
        if subdomains is None:
            print("domain,", domain, " is not a valid domain")
            return None
        nameserver = list()
        zone = list()
        cname = list()  # questa la lascio lista, al più rimane vuota ma non torna None
        dictList = list()
        print("Looking for zones ", domain, "depends on...")
        for domain in subdomains:
            nameserver = list()
            zone = None  # string
            cname = list()  # of string
            curName = domain
            cnamelist = list()
            alreadyResolved = False
            while True:
                check = self.cacheLookUp(curName, "CNAME")
                if check is None:
                    # non è in cache
                    break
                elif check.values == "NoAnswer" or check.values == "NXDomain":
                    if check.values == "NXDomain":
                        self.logError.append({"domain": curName, "error": "this domain does not exists: NXDomain"})
                        print("NXDomain")
                        break
                    else:
                        # se arrivo qui vuol dire che la catena di CNAME sfocia nel nulla, o meglio che non ci sono  cname, no answer
                        print("This CNAME has not alias")
                        break
                else:
                    if check.values[0] not in subdomains:
                        subdomains.append(check.values[0])
                    else:
                        for dix in dictList:
                            if dix["Zone"] == check.values[0]:
                                # l'ho già risolto
                                alreadyResolved = True
                                # ma verifico se c'è anche tale cname
                                alreadyCname = False
                                for cn in dix["CNAME"]:
                                    if cn == check.name:
                                        alreadyCname = True
                                        break
                                if not alreadyCname:
                                    dix["CNAME"].append(check.name)
                        break
                    cname.append(check.name)
                    cnamelist.append(check.name)
                    curName = check.values[0]
                    #fai qui check se curname è zona che hai già risolto aggiungici sto cname non ririsolverla
            if alreadyResolved:
                continue
            check = self.cacheLookUp(curName, "NS")
            if check is None:
                rr = findRRecord(curName, "NS")
                if rr is None:
                    # c'è stato errore da gestire tenere traccia
                    print("error of some kind in finding the rrecord")
                    self.logError.append({"domain": curName, "error": "Not found with dns.resolver"})
                    continue
                elif rr["Result"].values == "NoAnswer":
                    # non è nome di zona, proseguo e magari aggiungo in cache sta info OCCHIO QUI devi distinguere i due casi in cui non è zona o non esiste dominio
                    #print("Non è nome di zona: ", curName)
                    continue
                elif rr["Result"].values == "NXDomain":
                    print("Not an existing domain, ", curName)
                    continue
                else:
                    zone = rr["Result"].url
                    print("Depends on: ", zone)
                    check = rr["Result"]
                    self.cache.append(check)
                    if rr["CNAME"] is not None:
                        for l in rr["CNAME"]:
                            cname.append(l)
                            #qui dovrei controllare che non sia già in cache
                            self.cache.append(l)
                            subd = Resolver.subdomains(l.values[0], rootIncluded=False)
                            alreadySubdomain = False
                            for i in subd:
                                for su in subdomains:
                                    if su == i:
                                        alreadySubdomain = True
                                        break
                                if not alreadySubdomain:
                                    subdomains.append(i)
                                alreadySubdomain = False
                    # se ho già risolto non lo ririsolvo ma se ho trovato che ha dei cname ce li aggiungo
                    alreadyResolved = False
                    for dix in dictList:
                        if dix["Zone"] == zone:
                            # l'ho già risolto
                            alreadyResolved = True
                            # ma verifico se c'è anche tale cname
                            alreadyCname = False
                            if rr["CNAME"] is not None:
                                for l in rr["CNAME"]:
                                    for cn in dix["CNAME"]:
                                        if cn == l.url:
                                            alreadyCname = True
                                            break
                                    if not alreadyCname:
                                        dix["CNAME"].append(l.url)
                                    alreadyCname = False
                            break

                    if alreadyResolved:
                        continue
            elif check.values == "NoAnswer" or check.values == "NXDomain":
                # qualcosa non quadra non esiste sto nome di name server
                #print("non è nome di zona: ", curName)
                continue
            else:
                zone = check.name
                alreadyResolved = False
                dcElem = None
                #cerco se questa zona l'ho già risolta, potrei averlo fatto tramite cache e ora essere qui perché son passato da CNAME
                for dc in dictList:
                    if dc["Zone"] == zone:
                        alreadyResolved = True
                        dcElem = dc
                        break
                #ora verifico che anche se l'ho già risolta ha già tutti i cname di zona presi magari da cache
                if alreadyResolved:
                    if len(cnamelist) != 0:
                        alreadyCnameExist = False
                        for e in cnamelist:
                            for cn in dcElem["CNAME"]:
                                if cn.name == e.url:
                                    alreadyCnameExist = True
                                    break
                            if not alreadyCnameExist:
                                dcElem["CNAME"].append(e)
                            alreadyCnameExist = False
                    else:
                        continue

                #qui devi vedere se è già stata risolta questa zona, perché se non è stata risolta
                #perché c'è caso, vedi www.easupersian.com per cui tramite cache arrivo qui due volte e risolvo sta zona due volte
                #perché il cname indica un nome di zona che ho già risolto
                #qui invece fai check e aggiungici tutti i cname che hai trovato

            for ns in check.values:
                # Riprendi da qui devi fare parte in cui cerchi prima in cache il nameserver prima di cercarlo con query
                check = self.cacheLookUp(ns, "A")
                if check is None:
                    result = findRRecord(ns, "A")
                    if result is None:
                        # errore di qualche tipo da gestire, non è stato trovato il nameserver
                        self.logError.append({"domain": ns, "error": "Nameserver not found with dns.resolver"})
                        continue
                    elif result["Result"].values == "NoAnswer" or result["Result"].values == "NXDomain":
                        # errore non è nome di nameserver
                        self.cache.append(result["Result"])
                        self.logError.append({"domain": ns, "error": "Not a name of nameserver"})
                        continue
                    else:
                        nameserver.append(result["Result"])
                        self.cache.append(result["Result"])
                        # qui non faccio verifica di CNAME perchè da regole protocollo in NS non hanno alias
                        splittedNameServer = Resolver.subdomains(ns, rootIncluded=False)
                        for splt in splittedNameServer:
                            if splt not in subdomains:
                                subdomains.append(splt)
                elif check.values == "NoAnswer" or check.values == "NXDomain":
                    print("Error: nameserver doesn't exists, ", ns)
                    if check.values == "NXDomain":
                        self.logError.append({"domain": ns, "error" : "this domain does not exists: NXDomain"})
                    else:
                        self.logError.append({"domain": ns, "error": "Not a name of nameserver"})
                    continue
                else:
                    nameserver.append(check)
                    splittedNameServer = Resolver.subdomains(ns, rootIncluded=False)
                    for splt in splittedNameServer:
                        if splt not in subdomains:
                            subdomains.append(splt)

            dictList.append({"Zone": zone, "NameServers": nameserver, "CNAME": cname})

        return dictList


    def findDNSInfoMultiple(self, domainList):
        """
        This method calls the findDNSInfo method iterating on a list of domain.
        :param domainList: is a list of domains as strings.
        :return: a list of dictionaries, each of them has two keys. The first key is “Domain” the value of which is one of the domains in domainList as string. The second key is “DNSInfo” and its value is the list of dictionaries returned when the method findDNSInfo is called, so the keys of the dictionaries in this list are the same as findDNSInfo method, “Zones”,  “NameServers” and “CNAME” with the same purpose as in findDNSInfo method. In this way it is possible to the association between domain and the zones it depends on.
        """
        results = list()
        for el in domainList:
            dictionary = dict()
            #occhio che qui ora ritorna anche qualche record di tipo cname
            dictionary["DNSInfo"] = self.findDNSInfo(el)
            dictionary["Domain"] = el
            results.append(dictionary)

        return results


    @staticmethod
    def subdomains(domain,rootIncluded=False):
        """
        This method is a static method which splits a domain in subdomains and returns the list of subdomains as strings.
        :param domain: a string representing a domain. If domain is not in the fully qualified domain name notation it is transformed into such notation before it is splitted. If domain is not a domain because it includes some special char, then the method prints an error on screen and returns None.
        :param rootIncluded: a boolean. If rootIncluded is True the returned list also includes the root domain, default is False.
        :return: a list of string, each string is a subdomain of the domain in input.

        Example:
            list = Resolver.subdomains("www.example.com", rootIncluded = True)
            print(list) => ["www.example.com.", "example.com.", "com.", "."]
        """
        check = re.findall("[/@,#]", domain)
        if len(check) != 0:
            print(domain, " is not a valid domain.")
            return None

        if not domain.endswith("."):
            domain = domain + "."
        else:
            pass
        splittedList = domain.split(".")
        splittedList.pop(len(splittedList)-1)
        subdomains = list()
        currentDomain = "."
        subdomains.append(currentDomain)
        isFirst = True
        for el in reversed(splittedList):
            if isFirst:
                currentDomain = el + "."
                isFirst = False
            else:
                currentDomain = el + "." + currentDomain
            subdomains.append(currentDomain)
        if not rootIncluded:
            subdomains.pop(0)
        return subdomains

    def load(self, csv):
        """
        This method loads a cache from a .csv file. This method is called from the constructor of this class. This method initializes the field cache with a list of objects of RRecord class. If the .csv file is not found this method print a warning on screen and the field cache is not initialized.
        csv file has to be written in the following way. In each line has to be written a resource record. First the domain has to be written, then a comma followed by the type of the resource record, and in the end a list, comma separated, of values. For example:
            google.com, NS, ns1.google.com, ns2.google.com, ns3.google.com, ns4.google.com
        The value could be also the string “NoAnswer”, if there is no answer to the query with the corresponding name and type, or the string “NXDomain”, if the name is not an existing domain.
        :param csv: a name of a .csv file as string.
        :return: this method has no return value, instead it sets the cache field of the Resolver object from where it is called
        """
        fhand = open(csv, "r")
        for line in fhand:
            splitted = line.split("\t")     # \t is TAB
            if len(splitted) >= 3:
                if splitted[2].strip() == "NoAnswer" or splitted[2].strip() == "NXDomain":
                    self.cache.append(RRecord(splitted[0], splitted[1], splitted[2].strip()))
                    continue
                listRespose = list()
                for a in splitted[2:]:
                    listRespose.append(a.strip())
                rrecord = RRecord(splitted[0], splitted[1], listRespose)
                self.cache.append(rrecord)
            else:
                print("Line: ", line, " has too few arguments")
        fhand.close()

    def save(self, csv):
        """
        This method saves the content of the cache field on a .csv file. csv is the name of the file in which to save the cache. The .csv file is created or, if it already exists, it will be overwritten. The .csv file is written in the same way as it is described in load method.

        :param csv: the name of the .csv file in which to save the cache, as string.
        :return: this method has no return value, instead it create a .csv file.
        """
        fhand = open(csv, "w")
        line = ""
        for rr in self.cache:
            line = rr.url + "," + rr.type
            if rr.values == "NoAnswer":
                line = line + ",NoAnswer"
            elif rr.values == "NXDomain":
                line = line + ",NXDomain"
            else:
                for value in rr.values:
                    line = line + "," + value
            line = line + "\n"
            fhand.write(line)
        fhand.close()

    def cacheLookUp(self, name, type):
        """
        This method looks for the RRecord object with the corresponding name and type in the cache field of this method and returns it.
        :param name: a string representing the name of a dns query.
        :param type: a string representing the type of a dns query.
        :return: a RRecord object with the name, type and values found in cache field. This method returns None if there is no such RRecord object in cache.
        """
        found = False
        for rr in self.cache:
            if rr.url == name and rr.type == type:
                found = True
                return rr
        if not found:
            return None

    def saveLogError(self, name):
        """
        This method saves the error logs of the field logError on a .csv file. In each row of the file is written the domain which causes the error followed by the description of the error. The error are added to the file if the file already exists
        :param name: the name of a .csv file in which to save logError.
        :return: this method has no return value, instead it create or update a file
        """
        try:
            fhand = open(name, "a")
            if len(self.logError) == 0:
                print("No error occurred")
                return
            for each in self.logError:
                line = each["Domain"] + "," + each["Description"] +"\n"
                fhand.write(line)
            fhand.close()
        except:
            print("Error in opening file: ", name)
            return
