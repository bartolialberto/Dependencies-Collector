import re
import dns.resolver
from entities.ErrorLogger import ErrorLogger, ErrorEntry
from entities.LocalResolverCache import LocalResolverCache
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from utils import domain_name_utils
from utils import list_utils
from exceptions.UnknownReasonError import UnknownReasonError
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.NoRecordInCacheError import NoRecordInCacheError
from entities.Zone import Zone


def search_resource_records(resolver: dns.resolver.Resolver, name: str, _type: TypesRR):
    cname_rrecords = list()
    try:
        answer = resolver.resolve(name, _type.to_string())
        for cname in answer.chaining_result.cnames:
            temp = []
            for key in cname.items.keys():
                temp.append(key.target)
            debug = TypesRR.parse_from_string(dns.rdatatype.to_text(cname.rdtype))
            cname_rrecords.append(RRecord(cname.name, debug, temp))
        if len(cname_rrecords) == 0:  # no aliases found
            pass
        rrecords = list()
        for ad in answer:
            rrecords.append(ad.to_text())
        response_rrecords = RRecord(answer.canonical_name.to_text(), _type, rrecords)
        # risultato: tupla con:
        #       - RRecord di tipo ty con il risultato della query come campo RRecord.values
        #       - lista di RRecord per gli aliases attraversati per avere la risposta
        return response_rrecords, cname_rrecords
    except dns.resolver.NXDOMAIN:  # name is a domain that does not exist
        raise DomainNonExistentError(name)
    except dns.resolver.NoAnswer:  # there is no answer
        raise NoAnswerError(name, _type)
    # no non-broken nameservers are available to answer the question
    # query name is too long after DNAME substitution
    except (dns.resolver.NoNameservers, dns.resolver.YXDOMAIN) as e:
        raise UnknownReasonError(message=str(e))
    except Exception:  # fail because of another reason...
        raise UnknownReasonError()


# TODO
def search_domains_dns_dependencies(self, domain_list):
    results = list()
    for el in domain_list:
        dictionary = dict()
        #occhio che qui ora ritorna anche qualche record di tipo cname
        dictionary["DNSInfo"] = self.search_domain_dns_dependencies(el)
        dictionary["Domain"] = el
        results.append(dictionary)
    return results


def search_domain_dns_dependencies(resolver: dns.resolver.Resolver, domain: str) -> (list, LocalResolverCache, ErrorLogger):
    cache = LocalResolverCache()
    # cache.load_csv("C:\\Users\\fabbi\\PycharmProjects\\LavoroTesi\\testing\\output\\cache.csv")
    cache.load_csv("output\\cache.csv")
    error_logs = ErrorLogger()
    rr_response = None
    rr_aliases = None
    nsz_rr_response = None
    nsz_rr_alias = None
    check = re.findall("[/@,#]", domain)
    if len(check) != 0:
        raise InvalidDomainNameError(domain)
    # if domain contains caratteri strani return None e setta valore in logErrror o meglio basta verificare che subdomains non sia NOn
    subdomains = domain_name_utils.get_subdomains_name_list(domain, root_included=True)
    if subdomains is None:
        print("domain,", domain, " is not a valid domain")
        return None
    nameserver = list()
    zone_name = list()

    # lista degli alias per arrivare alla risposta della query NS
    cname = list()  # questa la lascio lista, al più rimane vuota ma non torna None

    zone_list = list()
    zone_list = list()  # si va a popolare con ogni iterazione
    print("Looking for zones ", domain, "depends on...")
    for domain in subdomains:
        # reset all variables for new iteration
        nameserver = list()     # nameserver of the zone
        zone_name = None
        cname = list()  # cnames of ... ?
        curr_name = domain
        cname_list = list()
        is_domain_already_resolved = False
        while True:
            try:
                cache_look_up = cache.look_up_first(curr_name, TypesRR.CNAME)  # se ci sono alias nella cache
                if cache_look_up.get_first_value() not in subdomains:
                    subdomains.append(cache_look_up.get_first_value())
                else:
                    for zone in zone_list:
                        if zone.name == cache_look_up.get_first_value():
                            # l'ho già risolto
                            is_domain_already_resolved = True
                            # ma verifico se c'è anche tale cname
                            already_cname = False
                            for cn in zone.cnames:
                                if cn == cache_look_up.name:
                                    already_cname = True
                                    break
                            if not already_cname:
                                zone.cnames.append(cache_look_up.name)
                    break
                cname.append(cache_look_up.name)
                cname_list.append(cache_look_up.name)
                curr_name = cache_look_up.values[0]
                # fai qui check se curname è zona che hai già risolto aggiungici sto cname non ririsolverla
            except NoRecordInCacheError:
                break
        if is_domain_already_resolved:
            continue
        try:
            cache_look_up = cache.look_up_first(curr_name, TypesRR.NS)      # ci si chiede se curr_name è nome di zona, il risultato sarà la lista di NSZ
            zone_name = cache_look_up.name
            is_domain_already_resolved = False
            dc_elem = None
            # cerco se questa zona l'ho già risolta, potrei averlo fatto tramite cache e ora essere qui perché son passato da CNAME
            for zone in zone_list:
                if zone.name == zone_name:
                    is_domain_already_resolved = True
                    dc_elem = zone
                    break
            # ora verifico che anche se l'ho già risolta ha già tutti i cname di zona presi magari da cache
            if is_domain_already_resolved:
                if len(cname_list) != 0:
                    cname_already_exists = False
                    for e in cname_list:
                        for cn in dc_elem.cnames:
                            if cn.name == e.name:
                                cname_already_exists = True
                                break
                        if not cname_already_exists:
                            dc_elem.cnames.append(e)
                        cname_already_exists = False
                else:
                    continue
        except NoRecordInCacheError:
            try:
                rr_response, rr_aliases = search_resource_records(resolver, curr_name, TypesRR.NS)
            except NoAnswerError:
                # non è nome di zona, proseguo e magari aggiungo in cache sta info OCCHIO QUI devi distinguere i due casi in cui non è zona o non esiste dominio
                # print("Non è nome di zona: ", curName)
                continue
            except DomainNonExistentError:
                print("Not an existing domain, ", curr_name)
                continue
            except UnknownReasonError:
                # c'è stato errore da gestire tenere traccia
                print("error of some kind in finding the rrecord")
                error_logs.add_entry({"domain": curr_name, "error": "Not found with dns.resolver"})
                continue
            # la query ns è andata a buon fine, ci sono dei risultati
            zone_name = rr_response.name
            print("Depends on: ", zone_name)
            cache.add_entry(rr_response)
            for alias in rr_aliases:
                cname.append(alias)
                list_utils.append_to_list_with_no_duplicates(cache.cache, alias)
                subd = domain_name_utils.get_subdomains_name_list(alias.values[0], root_included=False)
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
            is_domain_already_resolved = False
            for zone in zone_list:
                if zone.name == zone_name:
                    # l'ho già risolto
                    is_domain_already_resolved = True
                    # ma verifico se c'è anche tale cname
                    already_cname = False
                    if rr_aliases is not None:
                        for alias in rr_aliases:
                            for cn in zone.cnames:
                                if cn == alias.name:
                                    already_cname = True
                                    break
                            if not already_cname:
                                zone.cnames.append(alias.name)
                            already_cname = False
                    break
            if is_domain_already_resolved:
                continue
            # qui devi vedere se è già stata risolta questa zona, perché se non è stata risolta
            # perché c'è caso, vedi www.easupersian.com per cui tramite cache arrivo qui due volte e risolvo sta zona due volte
            # perché il cname indica un nome di zona che ho già risolto
            # qui invece fai check e aggiungici tutti i cname che hai trovato
        for nsz in rr_response.values: # per ogni NSZ della zona cerco di risolverlo
            # Riprendi da qui devi fare parte in cui cerchi prima in cache il nameserver prima di cercarlo con query
            try:
                nsz_rr_response = cache.look_up_first(nsz, TypesRR.A)
                nameserver.append(rr_response)
                # qui non faccio verifica di CNAME perchè da regole protocollo in NS non hanno alias
                split_name_server = domain_name_utils.get_subdomains_name_list(nsz, root_included=False)
                for ns in split_name_server:
                    if ns not in subdomains:
                        subdomains.append(ns)
            except NoRecordInCacheError:
                try:
                    nsz_rr_response, nsz_rr_alias = search_resource_records(resolver, nsz, TypesRR.A)
                except UnknownReasonError:
                    # errore di qualche tipo da gestire, non è stato trovato il nameserver
                    error_logs.add_entry({"domain": nsz, "error": "Nameserver not found with dns.resolver"})
                    continue
                except (NoAnswerError, DomainNonExistentError):
                    # errore non è nome di nameserver
                    cache.add_entry(nsz_rr_response)
                    error_logs.add_entry({"domain": nsz, "error": "Not a name of nameserver"})
                    continue
                nameserver.append(nsz_rr_response)
                cache.add_entry(nsz_rr_response)
                # qui non faccio verifica di CNAME perchè da regole protocollo in NS non hanno alias
                split_name_server = domain_name_utils.get_subdomains_name_list(nsz, root_included=False)
                for ns in split_name_server:
                    if ns not in subdomains:
                        subdomains.append(ns)
        tmp = Zone(zone_name, nameserver, cname)
        zone_list.append(tmp)
        # dict_list.append({"Zone": zone_name, "NameServers": nameserver, "CNAME": cname})
    # return dict_list
    return zone_list, cache, error_logs
