# coding=utf-8
import dns.resolver
from utils import domain_name_utils
from utils import list_utils
from exceptions.NoRecordInCacheError import NoRecordInCacheError
from exceptions.UnknownReasonError import UnknownReasonError
from Zones import RRecord
import re


class Resolver:
    cache = list()
    logError = list()

    def __init__(self, csv=None):
        if csv is None:
            self.cache = list()
            return
        try:
            self.load(csv)
        except IOError:
            print("Cache file passed as input is not found. File name: ", csv)
            exit(1)
            return

    def find_i_pand_cname(self, domain):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ["1.1.1.1"]
        if not domain.endswith("."):
            domain = domain + "."
        print("Searching for Ip addresses...")
        cname_domains = list()
        current_name = domain
        result_a = None
        cached = True
        while True:
            cache_rr = None
            try:
                cache_rr = self.cache_look_up(current_name, "CNAME")  # ritorna il primo risultato (RRecord) nella cache, sennò None
                if cache_rr.values != "NXDomain" and cache_rr.values != "NoAnswer":   # se va a buon fine e c'è un risultato
                    cname_domains.append(cache_rr)
                    current_name = cache_rr.values[0]
                else:
                    if cache_rr.values == "NXDomain":
                        self.logError.append({"domain": current_name, "error": "this domain does not exists: NXDomain"})
                        print("NXDomain")
                        break
                    else:
                        #se arrivo qui vuol dire che la catena di CNAME sfocia nel nulla, o meglio che non ci sono  cname, no answer
                        print("This CNAME has not alias")
                        break
            except NoRecordInCacheError:
                try:
                    cache_rr = self.cache_look_up(current_name, "A")
                    if cache_rr.values != "NXDomain" and cache_rr.values != "NoAnswer":
                        result_a = cache_rr
                        break
                    else:
                        result_a = "NotAHost"
                        break
                except NoRecordInCacheError:
                    cached = False
                    break
        if not cached:
            response_rrecords = None
            cname_rrecords = None
            try:
                response_rrecords, cname_rrecords = RRecord.find_resource_records(current_name, "A")
                result_a = response_rrecords

                # irrangiungibile???
                if cname_rrecords is not None:     # se ci sono alias aggiorna la cache
                    for rr in cname_rrecords:
                        try:
                            found = self.cache_look_up(rr.name, "CNAME")
                        except NoRecordInCacheError:
                            self.cache.append(rr)       # se non c'è nella cache aggiungilo
                        cname_domains.append(rr)
            except UnknownReasonError:
                print("error in find RRecord:")
                # qui dovrei tornare errore in qualche modo, far sapere che sto dominio torna errore
                self.logError.append({"domain": current_name, "error": "Not found with dns.resolver"})
            except dns.resolver.NXDOMAIN:
                self.cache.append(result_a)
                result_a = "NotAHost"
            except dns.resolver.NoAnswer:
                self.cache.append(result_a)
                result_a = "NotAHost"
        if len(cname_domains) == 0:
            cname_domains = None
        # ricorda che ips può tornare None se e solo se c'è stato errore nel findRRecord
        dictionary = {
            "IPs": result_a,
            "CNAMEs": cname_domains
        }
        print("{")
        print("    IPs: ", result_a)
        print("    CNAMEs: ", cname_domains)
        print("}")
        return dictionary

    def find_dns_info(self, domain):
        check = re.findall("[/@,#]", domain)
        if len(check) != 0:
            print("WebDomain is not a valid domain: ", domain)
            self.logError.append({"domain": domain, "error": "Not a valid domain"})
        res = dns.resolver.Resolver()
        res.nameservers = ["1.1.1.1"]
        # if domain contains caratteri strani return None e setta valore in logErrror o meglio basta verificare che subdomains non sia NOn
        subdomains = domain_name_utils.get_subdomains_name_list(domain, root_included=True)
        if subdomains is None:
            print("domain,", domain, " is not a valid domain")
            return None
        nameserver = list()
        zone = list()
        cname = list()  # questa la lascio lista, al più rimane vuota ma non torna None
        dict_list = list()
        print("Looking for zones ", domain, "depends on...")
        for domain in subdomains:
            nameserver = list()
            zone = None  # string
            cname = list()  # of string
            curr_name = domain
            cname_list = list()
            is_already_resolved = False
            while True:
                check = None
                try:
                    check = self.cache_look_up(curr_name, "CNAME")  # se ci sono alias nella cache
                    if check.values[0] not in subdomains:
                        subdomains.append(check.values[0])
                    else:
                        for dix in dict_list:
                            if dix["Zone"] == check.values[0]:
                                # l'ho già risolto
                                is_already_resolved = True
                                # ma verifico se c'è anche tale cname
                                already_cname = False
                                for cn in dix["CNAME"]:
                                    if cn == check.name:
                                        already_cname = True
                                        break
                                if not already_cname:
                                    dix["CNAME"].append(check.name)
                        break
                    cname.append(check.name)
                    cname_list.append(check.name)
                    curr_name = check.values[0]
                    # fai qui check se curname è zona che hai già risolto aggiungici sto cname non ririsolverla
                except NoRecordInCacheError:
                    break
            if is_already_resolved:
                continue
            try:
                check = self.cache_look_up(curr_name, "NS")
                zone = check.name
                is_already_resolved = False
                dc_elem = None
                #cerco se questa zona l'ho già risolta, potrei averlo fatto tramite cache e ora essere qui perché son passato da CNAME
                for dc in dict_list:
                    if dc["Zone"] == zone:
                        is_already_resolved = True
                        dc_elem = dc
                        break
                #ora verifico che anche se l'ho già risolta ha già tutti i cname di zona presi magari da cache
                if is_already_resolved:
                    if len(cname_list) != 0:
                        cname_already_exists = False
                        for e in cname_list:
                            for cn in dc_elem["CNAME"]:
                                if cn.name == e.name:
                                    cname_already_exists = True
                                    break
                            if not cname_already_exists:
                                dc_elem["CNAME"].append(e)
                            cname_already_exists = False
                    else:
                        continue
            except NoRecordInCacheError:
                try:
                    rr = RRecord.find_resource_records(curr_name, "NS")
                except dns.resolver.NoAnswer:
                    # non è nome di zona, proseguo e magari aggiungo in cache sta info OCCHIO QUI devi distinguere i due casi in cui non è zona o non esiste dominio
                    #print("Non è nome di zona: ", curName)
                    continue
                except dns.resolver.NXDOMAIN:
                    print("Not an existing domain, ", curr_name)
                    continue
                except UnknownReasonError:
                    # c'è stato errore da gestire tenere traccia
                    print("error of some kind in finding the rrecord")
                    self.logError.append({"domain": curr_name, "error": "Not found with dns.resolver"})
                    continue
                zone = rr["Result"].name
                print("Depends on: ", zone)
                check = rr["Result"]
                self.cache.append(check)
                if rr["CNAME"] is not None:     # se ci sono stati alias
                    for l in rr["CNAME"]:
                        cname.append(l)
                        list_utils.append_to_list_with_no_duplicates(self.cache, l)
                        subd = domain_name_utils.get_subdomains_name_list(l.values[0], root_included=False)
                        is_already_subdomain = False
                        for i in subd:
                            for su in subdomains:
                                if su == i:
                                    is_already_subdomain = True
                                    break
                            if not is_already_subdomain:
                                subdomains.append(i)
                            is_already_subdomain = False
                # se ho già risolto non lo ririsolvo ma se ho trovato che ha dei cname ce li aggiungo
                is_already_resolved = False
                for dix in dict_list:
                    if dix["Zone"] == zone:
                        # l'ho già risolto
                        is_already_resolved = True
                        # ma verifico se c'è anche tale cname
                        already_cname = False
                        if rr["CNAME"] is not None:
                            for l in rr["CNAME"]:
                                for cn in dix["CNAME"]:
                                    if cn == l.name:
                                        already_cname = True
                                        break
                                if not already_cname:
                                    dix["CNAME"].append(l.name)
                                already_cname = False
                        break
                if is_already_resolved:
                    continue
                # qui devi vedere se è già stata risolta questa zona, perché se non è stata risolta
                # perché c'è caso, vedi www.easupersian.com per cui tramite cache arrivo qui due volte e risolvo sta zona due volte
                # perché il cname indica un nome di zona che ho già risolto
                # qui invece fai check e aggiungici tutti i cname che hai trovato
            for ns in check.values:
                # Riprendi da qui devi fare parte in cui cerchi prima in cache il nameserver prima di cercarlo con query
                check = self.cache_look_up(ns, "A")
                if check is None:
                    result = RRecord.find_resource_records(ns, "A")
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
                        splittedNameServer = domain_name_utils.get_subdomains_name_list(ns, root_included=False)
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
                    splittedNameServer = domain_name_utils.get_subdomains_name_list(ns, root_included=False)
                    for splt in splittedNameServer:
                        if splt not in subdomains:
                            subdomains.append(splt)

            dict_list.append({"Zone": zone, "NameServers": nameserver, "CNAME": cname})
        return dict_list

    def find_dns_info_multiple(self, domain_list):
        results = list()
        for el in domain_list:
            dictionary = dict()
            #occhio che qui ora ritorna anche qualche record di tipo cname
            dictionary["DNSInfo"] = self.find_dns_info(el)
            dictionary["Domain"] = el
            results.append(dictionary)

        return results

    def load(self, csv):
        fhand = open(csv, "r")
        for line in fhand:
            splitted = line.split("\t")     # \t is TAB
            if len(splitted) >= 3:
                if splitted[2].strip() == "NoAnswer" or splitted[2].strip() == "NXDomain":
                    self.cache.append(RRecord(splitted[0], splitted[1], splitted[2].strip()))
                    continue
                list_respose = list()
                for a in splitted[2:]:
                    list_respose.append(a.strip())
                rrecord = RRecord(splitted[0], splitted[1], list_respose)
                self.cache.append(rrecord)
            else:
                print("Line: ", line, " has too few arguments")
        fhand.close()

    def save(self, csv):
        fhand = open(csv, "w")
        line = ""
        for rr in self.cache:
            line = rr.name + "," + rr.type
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

    def cache_look_up(self, name, typ):
        for rr in self.cache:
            if rr.name == name and rr.type == typ:
                return rr
        raise NoRecordInCacheError()

    def save_log_error(self, name):
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
