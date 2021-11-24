from typing import List
import dns.resolver
from dns.name import Name
from entities.DnsErrorLogger import DnsErrorLogger, DnsErrorEntry
from entities.LocalDnsResolverCache import LocalDnsResolverCache
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from entities.Zone import Zone
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.NoRecordInCacheError import NoRecordInCacheError
from exceptions.UnknownReasonError import UnknownReasonError
from utils import domain_name_utils, list_utils


class DnsResolver:
    '''
    resolver: dns.resolver.Resolver
    cache: LocalResolverCache
    error_logs: ErrorLogger
    '''

    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        self.cache = LocalDnsResolverCache()
        self.error_logs = DnsErrorLogger()

    def search_resource_records(self, name: str, type_rr: TypesRR) -> tuple:
        cname_rrecords = list()
        try:
            answer = self.resolver.resolve(name, type_rr.to_string())
            for cname in answer.chaining_result.cnames:
                temp = []
                for key in cname.items.keys():
                    temp.append(str(key.target))        # ORIGINAL: key.target
                debug = TypesRR.parse_from_string(dns.rdatatype.to_text(cname.rdtype))
                cname_rrecords.append(RRecord(cname.name, debug, temp))
            rr_values = list()
            for ad in answer:
                if isinstance(ad, Name):
                    rr_values.append(str(ad))
                else:
                    rr_values.append(ad.to_text())
            response_rrecords = RRecord(answer.canonical_name.to_text(), type_rr, rr_values)
            # risultato: tupla con:
            #       - RRecord di tipo ty con il risultato della query come campo RRecord.values
            #       - lista di RRecord per gli aliases attraversati per avere la risposta
            return response_rrecords, cname_rrecords
        except dns.resolver.NXDOMAIN:  # name is a domain that does not exist
            raise DomainNonExistentError(name)
        except dns.resolver.NoAnswer:  # there is no answer
            raise NoAnswerError(name, type_rr)
        # no non-broken nameservers are available to answer the question
        # query name is too long after DNAME substitution
        except (dns.resolver.NoNameservers, dns.resolver.YXDOMAIN) as e:
            raise UnknownReasonError(message=str(e))
        except Exception as e:  # fail because of another reason...
            raise UnknownReasonError(message=str(e))

    def search_multiple_domains_dependencies(self, domain_list: List[str]) -> dict:
        if len(domain_list) == 0:
            raise ValueError
        results = dict()
        # All other iteration
        for domain in domain_list:  # from index 1
            try:
                results[domain] = self.search_domain_dependencies(domain)
            except InvalidDomainNameError:
                pass
        return results

    def search_domain_dependencies(self, domain: str) -> List[Zone]:
        domain_name_utils.grammatically_correct(domain)
        error_logs = DnsErrorLogger()
        start_cache_length = len(self.cache.cache)
        subdomains = domain_name_utils.get_subdomains_name_list(domain, root_included=True)
        if len(subdomains) == 0:
            raise InvalidDomainNameError(domain)  # giusto???
        zone_list = list()  # si va a popolare con ogni iterazione
        print(f"Cache has {start_cache_length} entries.")
        print(f"Looking at zone dependencies for '{domain}'..")
        for domain in subdomains:
            # reset all variables for new iteration
            rr_response = None
            current_zone_nameservers = list()  # nameservers of the current zone
            current_zone_name = None
            path_cnames = list()
            current_zone_cnames = list()
            current_name = domain
            is_domain_already_solved = False
            # Controllo in cache se degli alias del curr_name ce ne sono già di risolti.
            # In caso positivo procedo al prossimo curr_name.
            # In caso negativo aggiungo (in fondo) l'alias alla lista subdomains per essere poi risolto.
            while True:
                try:
                    cache_look_up = self.cache.look_up_first(current_name, TypesRR.CNAME)  # nella cache ci saranno record cname solo perché saranno messi come cname appartenenti ad una zona
                except NoRecordInCacheError:
                    break
                if cache_look_up.get_first_value() not in subdomains:
                    subdomains.append(cache_look_up.get_first_value())
                else:
                    # curr_name è nome di zona ed è già stato risolto?
                    for zone in zone_list:
                        if zone.name == cache_look_up.get_first_value():
                            is_domain_already_solved = True
                            list_utils.append_with_no_duplicates(zone.cnames, cache_look_up.name)
                current_zone_cnames.append(cache_look_up)
                path_cnames.append(cache_look_up.name)
                # continua il ciclo while True seguendo la catena di CNAME
                current_name = cache_look_up.get_first_value()
            if is_domain_already_solved:
                continue
            # Ora curr_name potrebbe essere una cosa diversa rispetto domain. E' meglio così perché sarebbe inutile fare la query NS su un alias (vero???)
            # E se è diverso vuol dire che la ricerca con query DNS è stata già fatta? CONTROLLARE QUESTA EVENTUALITA'
            # Cerchiamo informazioni se curr_name è un nome di zona
            try:
                cache_look_up = self.cache.look_up_first(current_name, TypesRR.NS)
                # curr_name è quindi nome di zona
                is_domain_already_solved, tmp = DnsResolver.check_zone_list_by_name(zone_list, cache_look_up.name)  # quindi l'elaborazione qunado è stata fatta facendo la query è arriavata fino in fondo
                # VERIFICA D'INTEGRITA' per tutti i cname della zona... Evitiamo per adesso (vedere file vecchi per ripristinare)
                # Oppure è una sorta anche di aggiornamento di cname nuovi trovati per la zona???
                if is_domain_already_solved:
                    zone = tmp
                    is_cname_already_there = False
                    if len(path_cnames) != 0:
                        for path_cname in path_cnames:
                            for zone_cname in zone.cnames:
                                if path_cname == zone_cname:
                                    is_cname_already_there = True
                                    break
                                if not is_cname_already_there:
                                    zone.cnames.append(path_cname)
                                is_cname_already_there = False  # reset
                    else:
                        continue
                rr_response = cache_look_up
                authoritative_answer = False
            except NoRecordInCacheError:
                try:
                    rr_response, rr_aliases = self.search_resource_records(current_name, TypesRR.NS)
                    for alias in rr_aliases:
                        current_zone_cnames.append(alias)
                        list_utils.append_with_no_duplicates(self.cache.cache, alias)
                        alias_subdomains = domain_name_utils.get_subdomains_name_list(alias.get_first_value(),
                                                                                      root_included=False)
                        for alias_subdomain in alias_subdomains:
                            list_utils.append_with_no_duplicates(subdomains, alias_subdomain)
                    list_utils.append_with_no_duplicates(self.cache.cache, rr_response)
                    authoritative_answer = True
                except (UnknownReasonError, DomainNonExistentError) as e:
                    error_logs.add_entry(DnsErrorEntry(current_name, TypesRR.NS.to_string(), e.message))
                    continue
                except NoAnswerError:
                    continue  # is not a real error, it means is not a name for a zone
            current_zone_name = rr_response.name
            if authoritative_answer:
                print(f"Depends on zone: {current_zone_name}")
            else:
                print(f"Depends on zone: {current_zone_name}    [NON-AUTHORITATIVE]")
            is_domain_already_solved, tmp = DnsResolver.check_zone_list_by_name(zone_list, current_zone_name)
            if is_domain_already_solved:
                continue
            for nsz in rr_response.values:  # per ogni NSZ della zona cerco di risolverlo
                try:
                    nsz_rr_response = self.cache.look_up_first(nsz, TypesRR.A)
                except NoRecordInCacheError:
                    try:
                        nsz_rr_response, nsz_rr_alias = self.search_resource_records(nsz, TypesRR.A)
                        list_utils.append_with_no_duplicates(self.cache.cache, nsz_rr_response)
                    except (UnknownReasonError, NoAnswerError, DomainNonExistentError) as e:
                        error_logs.add_entry(DnsErrorEntry(nsz, TypesRR.A, e.message))
                        continue
                current_zone_nameservers.append(nsz_rr_response)
                # qui non faccio verifica di CNAME perchè da regole protocollo in NS non hanno alias
                split_name_server = domain_name_utils.get_subdomains_name_list(nsz, root_included=False)
                for ns in split_name_server:
                    if ns not in subdomains:
                        subdomains.append(ns)
            zone_list.append(Zone(current_zone_name, current_zone_nameservers, current_zone_cnames))
        print(
            f"Dependencies recap: {len(zone_list)} zones, {len(self.cache.cache) - start_cache_length} cache entries added, {len(error_logs.logs)} errors.\n")
        return zone_list

    def export_all(self) -> None:
        self.cache.write_to_csv_in_output_folder()
        self.error_logs.write_to_csv_in_output_folder()

    @staticmethod
    def check_zone_list_by_name(zone_list: List[Zone], zone_name: str) -> (bool, Zone):
        for zone in zone_list:
            if zone.name == zone_name:
                return True, zone
        return False, None
