from typing import List, Tuple
import dns.resolver
from dns.name import Name
from entities.DnsErrorLogger import DnsErrorLogger, DnsErrorEntry
from entities.LocalDnsResolverCache import LocalDnsResolverCache
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from entities.Zone import Zone
from entities.error_log.ErrorLog import ErrorLog
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

    def search_resource_records_OLD(self, name: str, type_rr: TypesRR) -> Tuple[RRecord, RRecord]:
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

    def search_resource_records(self, name: str, type_rr: TypesRR) -> Tuple[RRecord, RRecord]:
        cname_rrecords = list()
        try:
            answer = self.resolver.resolve(name, type_rr.to_string())
            rr_aliases = list()
            for cname in answer.chaining_result.cnames:
                for key in cname.items.keys():
                    rr_aliases.append(str(key.target))        # ORIGINAL: key.target
                debug = TypesRR.parse_from_string(dns.rdatatype.to_text(cname.rdtype))
                if debug is TypesRR.CNAME:
                    print(f"DEBUG-IMPORTANTE: debug is CNAME! from={name} cnames={rr_aliases}")
                else:
                    print(f"DEBUG-IMPORTANTE: debug is NOT CNAME...")
            cname_rrecords = RRecord(name, TypesRR.CNAME, rr_aliases)
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

    def search_multiple_domains_dependencies_OLD(self, domain_list: List[str]) -> dict:
        if len(domain_list) == 0:
            raise ValueError
        results = dict()
        # All other iteration
        for domain in domain_list:  # from index 1
            try:
                results[domain] = self.search_domain_dependencies_OLD(domain)
            except InvalidDomainNameError:
                pass
        return results

    def search_multiple_domains_dependencies(self, domain_list: List[str]) -> tuple:
        results = dict()
        error_logs = list()
        for domain in domain_list:
            try:
                dns_result, logs = self.search_domain_dependencies(domain)
                results[domain] = dns_result
                for log in logs:
                    list_utils.append_with_no_duplicates(error_logs, log)
            except InvalidDomainNameError:
                pass
        return results, error_logs

    def search_domain_dependencies_OLD(self, domain: str) -> List[Zone]:
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
                            list_utils.append_with_no_duplicates(zone.aliases, cache_look_up.name)
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
                is_domain_already_solved, tmp = DnsResolver.check_zone_list_by_name(zone_list, cache_look_up.name)  # quindi l'elaborazione quando è stata fatta facendo la query è arrivata fino in fondo
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
                    rr_response, rr_aliases = self.search_resource_records_OLD(current_name, TypesRR.NS)
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
                        nsz_rr_response, nsz_rr_alias = self.search_resource_records_OLD(nsz, TypesRR.A)
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
        print(f"Dependencies recap: {len(zone_list)} zones, {len(self.cache.cache) - start_cache_length} cache entries added, {len(error_logs.logs)} errors.\n")
        return zone_list

    def search_domain_dependencies(self, domain: str) -> Tuple[List[Zone], List[ErrorLog]]:
        domain_name_utils.grammatically_correct(domain)
        error_logs = list()
        start_cache_length = len(self.cache.cache)
        subdomains = domain_name_utils.get_subdomains_name_list(domain, root_included=True)
        if len(subdomains) == 0:
            raise InvalidDomainNameError(domain)  # giusto???
        zone_list = list()  # si va a popolare con ogni iterazione
        print(f"Cache has {start_cache_length} entries.")
        print(f"Looking at zone dependencies for '{domain}'..")
        for current_domain in subdomains:
            if len(self.cache.cache) >= 67:
                print(f"", end='')
                pass
            # reset all variables for new iteration
            current_zone_nameservers = list()  # nameservers (of zone) of the current zone
            current_zone_cnames = list()
            current_zone_name = '_'
            # is domain a nameserver with aliases?
            try:
                tmp = self.cache.look_up_first_alias(current_domain)
                rr_a = self.cache.resolve_path_from_alias(current_domain)
                try:
                    rrs_cache = self.cache.look_up_zone_from_nameserver(rr_a.name)  # dovrei catturare l'eccezione, ma lo scenario non dovrebbe mai accadere
                    for zone in rrs_cache:
                        print(f">DEBUG: '{current_domain}' belongs to '{zone}', already resolved.")
                    continue
                except NoRecordInCacheError:
                    pass
            except NoRecordInCacheError:
                try:
                    rr_zone_values, rr_zone_aliases = self.search_resource_records(current_domain, TypesRR.CNAME)
                    self.cache.add_entry(rr_zone_values)
                    if len(rr_zone_aliases.values) != 0:
                        self.cache.add_entry(rr_zone_aliases)
                except NoAnswerError as e:
                    pass
                except (DomainNonExistentError, UnknownReasonError) as e:
                    error_logs.append(ErrorLog(e, current_domain, str(e)))
            # is domain a zone name?
            try:
                rr_ns = self.cache.look_up_first(current_domain, TypesRR.NS)
                current_zone_name, current_zone_nameservers, current_zone_cnames = self.cache.resolve_zone_from_zone_name(rr_ns)  # raise NoRecordInCacheError too
                for rr in current_zone_nameservers:
                    DnsResolver.split_domain_name_and_add_to_list(subdomains, rr.name, False)
                print(f"Depends on zone: {current_zone_name}\t\t\t[NON-AUTHORITATIVE]")
            except NoRecordInCacheError:
                try:
                    rr_zone_values, rr_zone_aliases = self.search_resource_records(current_domain, TypesRR.NS)
                except NoAnswerError as e:
                    # log error???
                    # current_name non è niente???
                    continue
                except (DomainNonExistentError, UnknownReasonError) as e:
                    error_logs.append(ErrorLog(e, current_domain, str(e)))
                    continue
                current_zone_name = rr_zone_values.name
                self.cache.add_entry(rr_zone_values)
                # no rr_aliases poiché una query NS non può avere alias
                for nameserver in rr_zone_values.values:
                    # per ogni nameserver devo considerare che potrebbero esserci già dei RR di tipo A ed il nameserver
                    # corrente è solo un alias di uno di quei nameserver che ha già (appunto) rr di tipo A nella cache,
                    # quindi in verità è già risolto (==> non server metterlo in cache, sennò ho doppioni)
                    try:
                        rr_a_cache = self.cache.look_up_a_query_with_all_aliases(nameserver)
                        list_utils.append_with_no_duplicates(current_zone_nameservers, rr_a_cache)  # ma se il RR ha solo il campo values diverso?
                    except NoRecordInCacheError:
                        try:
                            rr_nameserver_values, rr_nameserver_aliases = self.search_resource_records(nameserver, TypesRR.A)
                            try:
                                self.cache.look_up_from_list(rr_nameserver_aliases.values, TypesRR.A)
                                # already resolved. Nothing to do
                            except NoRecordInCacheError:
                                self.cache.add_entry(rr_nameserver_values)
                            if len(rr_nameserver_aliases.values) != 0:
                                self.cache.add_entry(rr_nameserver_aliases)
                                list_utils.append_with_no_duplicates(current_zone_cnames, rr_nameserver_aliases)
                            list_utils.append_with_no_duplicates(current_zone_nameservers, rr_nameserver_values)  # ma se il RR ha solo il campo values diverso?
                        except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as exc:
                            error_logs.append(ErrorLog(exc, current_domain, str(exc)))
                    DnsResolver.split_domain_name_and_add_to_list(subdomains, nameserver, False)
                print(f"Depends on zone: {current_zone_name}")
            zone_list.append(Zone(current_zone_name, current_zone_nameservers, current_zone_cnames))
        print(f"Dependencies recap: {len(zone_list)} zones, {len(self.cache.cache) - start_cache_length} cache entries added, {len(error_logs)} errors.\n")
        return zone_list, error_logs

    def export_all(self) -> None:
        self.cache.write_to_csv_in_output_folder()
        self.error_logs.write_to_csv_in_output_folder()

    @staticmethod
    def split_domain_name_and_add_to_list(_list: list, domain_name: str, root_included: bool):
        split = domain_name_utils.get_subdomains_name_list(domain_name, root_included=root_included)
        for sub_domain in split:
            if sub_domain not in _list:
                _list.append(sub_domain)
                # list_utils.append_with_no_duplicates(_list, sub_domain)

    @staticmethod
    def check_zone_list_by_name(zone_list: List[Zone], zone_name: str) -> (bool, Zone):
        for zone in zone_list:
            if zone.name == zone_name:
                return True, zone
        return False, None
