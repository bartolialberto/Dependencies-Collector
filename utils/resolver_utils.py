import re
import dns.resolver
from entities.ErrorLogger import ErrorLogger
from entities.LocalResolverCache import LocalResolverCache
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
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
        answer = resolver.resolve(name, _type.value)
        for cname in answer.chaining_result.cnames:
            temp = []
            for key in cname.items.keys():
                temp.append(key.target)
            cname_rrecords.append(RRecord(cname.name, TypesRR.parse_from_string(dns.rdatatype.to_text(cname.rdtype)), temp))
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
        raise NoAnswerError(name, _type.value)
    except Exception:  # fail because of another reason...
        raise UnknownReasonError()


def find_dns_info(resolver: dns.resolver.Resolver, domain: str):
    cache = LocalResolverCache()
    error_logs = ErrorLogger()
    rr_response = None
    rr_aliases = None
    nsz_rr_response = None
    nsz_rr_alias = None

    check = re.findall("[/@,#]", domain)
    if len(check) != 0:
        print("WebDomain is not a valid domain: ", domain)
        error_logs.add_entry({"domain": domain, "error": "Not a valid domain"})
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
    dict_list = list()  # si va a popolare con ogni iterazione
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
                if cache_look_up.values[0] not in subdomains:
                    subdomains.append(cache_look_up.values[0])
                else:
                    for dix in dict_list:
                        if dix["Zone"] == cache_look_up.values[0]:
                            # l'ho già risolto
                            is_domain_already_resolved = True
                            # ma verifico se c'è anche tale cname
                            already_cname = False
                            for cn in dix["CNAME"]:
                                if cn == cache_look_up.name:
                                    already_cname = True
                                    break
                            if not already_cname:
                                dix["CNAME"].append(cache_look_up.name)
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
            for dc in dict_list:
                if dc["Zone"] == zone_name:
                    is_domain_already_resolved = True
                    dc_elem = dc
                    break
            # ora verifico che anche se l'ho già risolta ha già tutti i cname di zona presi magari da cache
            if is_domain_already_resolved:
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
            for dix in dict_list:
                if dix["Zone"] == zone_name:
                    # l'ho già risolto
                    is_domain_already_resolved = True
                    # ma verifico se c'è anche tale cname
                    already_cname = False
                    if rr_aliases is not None:
                        for alias in rr_aliases:
                            for cn in dix["CNAME"]:
                                if cn == alias.name:
                                    already_cname = True
                                    break
                            if not already_cname:
                                dix["CNAME"].append(alias.name)
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
        zone_list.append(Zone(zone_name, nameserver, cname))
        # dict_list.append({"Zone": zone_name, "NameServers": nameserver, "CNAME": cname})
    # return dict_list
    return zone_list
