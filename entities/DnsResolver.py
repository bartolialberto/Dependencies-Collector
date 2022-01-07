from typing import List, Tuple, Dict, Set
import dns.resolver
from dns.name import Name
from entities.LocalDnsResolverCache import LocalDnsResolverCache
from entities.RRecord import RRecord
from entities.TLDPageScraper import TLDPageScraper
from entities.TypesRR import TypesRR
from entities.Zone import Zone
from entities.error_log.ErrorLog import ErrorLog
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoRecordInCacheError import NoRecordInCacheError
from exceptions.UnknownReasonError import UnknownReasonError
from utils import domain_name_utils, list_utils, email_address_utils


# TODO: documentazione
class DnsResolver:
    """
    This class represents a simple DNS resolver for the application. Is based on a real and complete DNS resolver from
    the 'dnspython' module.

    ...

    Attributes
    ----------
    resolver : DnsResolver
        The real and complete DNS resolver from the dnpython module.
    cache : LocalDnsResolverCache
        The cache used to handle requests.
    """
    def __init__(self, tld_list: List[str]):
        """
        Instantiate this DnsResolver object.

        """
        self.resolver = dns.resolver.Resolver()
        self.cache = LocalDnsResolverCache()
        self.tld_list = tld_list

    def do_query(self, name: str, type_rr: TypesRR) -> Tuple[RRecord, List[RRecord]]:
        """
        This method executes a real DNS query. It takes the domain name and the type as parameters.
        The result is a RR containing all the values in the values field, and another RR of type CNAME containing (in
        the values field) all the aliases found in the resolving path. If the latter has no aliases then the RR has an
        empty values field.

        :param name: Name parameter.
        :type name: str
        :param type_rr: Type of the query.
        :type type_rr: TypesRR
        :raise DomainNonExistentError: If the name refers to a non existent domain.
        :raise NoAnswerError: If the query has no answer.
        :raise UnknownReasonError: If no non-broken nameservers are available to answer the question, or if the query
        name is too long after DNAME substitution.
        :return: A tuple with 2 RR: one with the results, and the other with the aliases
        :rtype: Tuple[RRecord, RRecord]
        """
        try:
            answer = self.resolver.resolve(name, type_rr.to_string())
            rr_aliases = list()
            final_name = None
            for cname in answer.chaining_result.cnames:
                for key in cname.items.keys():
                    # rr_aliases.append(str(key.target))
                    name = str(cname.name)
                    alias_value = str(key.target)
                    rr_aliases.append(RRecord(name, TypesRR.CNAME, alias_value))
                    final_name = alias_value
                # check (useless) that type is CNAME
                '''
                try:
                    t = TypesRR.parse_from_string(dns.rdatatype.to_text(cname.rdtype))
                except NotResourceRecordTypeError:
                    raise
                if debug == TypesRR.CNAME:
                    print(f"DEBUG-IMPORTANTE: debug is CNAME! from={name} cnames={rr_aliases}")
                else:
                    print(f"DEBUG-IMPORTANTE: debug is NOT CNAME...")
                '''
            if final_name is None:
                final_name = name
            rr_values = list()
            for ad in answer:
                if isinstance(ad, Name):
                    rr_values.append(str(ad))
                else:
                    rr_values.append(ad.to_text())
            response_rrecord = RRecord(final_name, type_rr, rr_values)
            # response_rrecord = RRecord(answer.canonical_name.to_text(), type_rr, rr_values)
            return response_rrecord, rr_aliases
        except dns.resolver.NXDOMAIN:  # name is a domain that does not exist
            raise DomainNonExistentError(name)
        except dns.resolver.NoAnswer:  # there is no answer
            raise NoAnswerError(name, type_rr)
        except (dns.resolver.NoNameservers, dns.resolver.YXDOMAIN) as e:
            raise UnknownReasonError(message=str(e))
        except Exception as e:  # fail because of another reason...
            raise UnknownReasonError(message=str(e))

    def resolve_multiple_domains_dependencies(self, domain_list: List[str], reset_cache_per_elaboration=False) -> Tuple[Dict[str, List[Zone]], Dict[str, List[Zone]], Dict[str, List[str]], List[ErrorLog]]:
        """
        This method resolves the zone dependencies of a list of domain names.

        :param domain_list: A list of domain names.
        :type domain_list: List[str]
        :raise :
        :return: A tuple containing a dictionary in which each key is a domain name of the domain names list parameter,
        and the value is the list of zone; as second element of the tuple there's the list of error logs.
        :rtype: Tuple[Dict[str: List[Zone]], List[ErrorLog]]
        """
        results = dict()
        error_logs = list()
        zone_links = dict()
        nameservers = dict()
        for domain in domain_list:
            try:
                if reset_cache_per_elaboration:
                    self.cache.clear()

                dns_result, temp_zone_links, temp_nameservers, temp_logs = self.resolve_domain_dependencies(domain)

                # insert domain dns dependencies
                results[domain] = dns_result

                # merge zone dependencies
                zone_links.update(temp_zone_links)

                # merge nameservers
                nameservers.update(temp_nameservers)

                # merge error logs
                for log in temp_logs:
                    # list_utils.append_with_no_duplicates(error_logs, log)
                    error_logs.append(log)

            except InvalidDomainNameError:
                pass

        return results, zone_links, nameservers, error_logs

    def resolve_mailservers(self, mail_domain: str) -> List[str]:
        # TODO: docs
        try:
            domain_name_utils.grammatically_correct(mail_domain)
        except InvalidDomainNameError:
            try:
                email_address_utils.grammatically_correct(mail_domain)
            except InvalidDomainNameError:
                raise
        result = list()
        try:
            mx_values, mx_aliases = self.do_query(mail_domain, TypesRR.MX)
        except NoAnswerError:
            raise
        except (DomainNonExistentError, UnknownReasonError) as e:
            raise
        for value in mx_values.values:
            result.append(value)
        return result

    def resolve_domain_dependencies(self, domain: str):
        """
        This method resolves the zone dependencies of a domain name.
        It returns a list containing the zones and a list of error logs encountered during the elaboration.

        :param domain: A domain name.
        :type domain: str
        :param is_mail_domain: Flag that says if the domain has to be considered as mail domain.
        :type is_mail_domain: bool
        :raise :
        :return: The list of zone dependencies and the list of error logs, put together in a tuple.
        :rtype: Tuple[List[Zone], List[ErrorLog]]
        """
        try:
            domain_name_utils.grammatically_correct(domain)
        except InvalidDomainNameError:
            try:
                email_address_utils.grammatically_correct(domain)
            except InvalidDomainNameError:
                raise

        #
        zone_links = dict()     # to keep track of dependencies between zones
        nameservers = dict()
        error_logs = list()
        start_cache_length = len(self.cache.cache)
        subdomains = domain_name_utils.get_subdomains_name_list(domain, root_included=True)
        if len(subdomains) == 0:
            raise InvalidDomainNameError(domain)  # giusto???
        zone_list = list()  # si va a popolare con ogni iterazione
        print(f"Cache has {start_cache_length} entries.")
        print(f"Looking at zone dependencies for '{domain}'..")
        for current_domain in subdomains:
            # reset all variables for new iteration
            current_zone_nameservers = list()
            current_zone_cnames = list()
            current_zone_name = '_'
            rr_ns_answer = None
            rr_ns_aliases = None
            rr_cname_answer = None
            rr_cname_aliases = None
            rr_ns = None
            zone_name_of_nameserver = None

            # is domain a nameserver with aliases?
            try:
                rr_aliases = self.cache.lookup(current_domain, TypesRR.CNAME)
                aliases = set(map(lambda x: x.get_first_value(), rr_aliases))
                for alias in aliases:
                    self._split_domain_name_and_add_to_list(subdomains, alias, root_included=False)
                zone_names = self.cache.resolve_zones_from_nameserver(current_domain)
                for zone_name in zone_names:
                    tmp = list(map(lambda z: z.name, zone_list))
                    if zone_name not in tmp:
                        r = self.cache.resolve_zone_from_zone_name(zone_name)
                        zone = Zone(r[0], r[1], r[2])
                        zone_list.append(zone)
                        print(f"Depends on zone: {zone.name}\t\t\t[NON-AUTHORITATIVE]")
                        for nm in zone.nameservers:
                            self._split_domain_name_and_add_to_list(subdomains, nm.name, False)
            except (NoRecordInCacheError, NoAvailablePathError):
                try:
                    rr_cname_answer, rr_cname_aliases = self.do_query(current_domain, TypesRR.CNAME)
                    self.cache.add_entry(rr_cname_answer)
                    for rr in rr_cname_aliases:
                        self.cache.add_entry(rr)
                    self._split_domain_name_and_add_to_list(subdomains, rr_cname_answer.get_first_value(), root_included=False)
                    # resolving alias
                    n = rr_cname_answer.get_first_value()
                    try:
                        rr_a_answer, rr_a_aliases = self.do_query(n, TypesRR.A)
                        self.cache.add_entry(rr_a_answer)
                        for r in rr_a_aliases:
                            self.cache.add_entry(r)
                    except NoAnswerError:
                        pass
                    except (DomainNonExistentError, UnknownReasonError) as e:
                        error_logs.append(ErrorLog(e, current_domain, str(e)))
                except NoAnswerError:
                    pass        # fare query A????
                except (DomainNonExistentError, UnknownReasonError) as e:
                    error_logs.append(ErrorLog(e, current_domain, str(e)))

            # is domain a zone name?
            try:
                rr_ns = self.cache.lookup_first(current_domain, TypesRR.NS)
                current_zone_name, current_zone_nameservers, current_zone_cnames = self.cache.resolve_zone_from_ns_rr(rr_ns)  # raise NoRecordInCacheError too

                #
                self._init_dict_key_with_an_empty_set(zone_links, current_domain)

                for rr in current_zone_nameservers:
                    self._split_domain_name_and_add_to_list(subdomains, rr.name, False)

                    #
                    try:
                        zone_name_of_nameserver = self.resolve_zone_of_nameserver(rr.name)
                        zone_links[current_domain].add(zone_name_of_nameserver)
                    except ValueError:
                        pass
                    self._init_dict_key_with_an_empty_set_and_then_add(nameservers, rr.name, current_zone_name)

                zone = Zone(current_zone_name, current_zone_nameservers, current_zone_cnames)
                if zone not in zone_list:
                    print(f"Depends on zone: {current_zone_name}\t\t\t[NON-AUTHORITATIVE]")
                    zone_list.append(zone)
            except NoRecordInCacheError:
                try:
                    rr_ns_answer, rr_ns_aliases = self.do_query(current_domain, TypesRR.NS)
                except NoAnswerError:
                    # log error???
                    # current_name non è niente???
                    continue
                except (DomainNonExistentError, UnknownReasonError) as e:
                    error_logs.append(ErrorLog(e, current_domain, str(e)))
                    continue
                current_zone_name = rr_ns_answer.name
                self.cache.add_entry(rr_ns_answer)

                #
                self._init_dict_key_with_an_empty_set(zone_links, current_domain)

                # no rr_aliases poiché una query NS non può avere alias
                for nameserver in rr_ns_answer.values:
                    # per ogni nameserver devo considerare che potrebbero esserci già dei RR di tipo A ed il nameserver
                    # corrente è solo un alias di uno di quei nameserver che ha già (appunto) rr di tipo A nella cache,
                    # quindi in verità è già risolto (==> non server metterlo in cache, sennò ho doppioni)
                    try:
                        rr_a_cache = self.cache.resolve_path_also_from_alias(nameserver)
                        list_utils.append_with_no_duplicates(current_zone_nameservers, rr_a_cache)  # ma se il RR ha solo il campo values diverso?
                    except (NoRecordInCacheError, NoAvailablePathError):
                        try:
                            rr_a_answer, rr_a_aliases = self.do_query(nameserver, TypesRR.A)
                            try:
                                temp = list(map(lambda r: r.get_first_value(), rr_a_aliases))
                                self.cache.lookup_from_list(temp, TypesRR.A)
                                # already resolved. Nothing to do
                            except NoRecordInCacheError:
                                self.cache.add_entry(rr_a_answer)
                            for rr in rr_a_aliases:
                                self.cache.add_entry(rr)
                                list_utils.append_with_no_duplicates(current_zone_cnames, rr)
                            list_utils.append_with_no_duplicates(current_zone_nameservers, rr_a_answer)  # ma se il RR ha solo il campo values diverso?
                        except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as exc:
                            error_logs.append(ErrorLog(exc, current_domain, str(exc)))
                    self._split_domain_name_and_add_to_list(subdomains, nameserver, False)

                    #
                    try:
                        zone_name_of_nameserver = self.resolve_zone_of_nameserver(nameserver)
                        zone_links[current_domain].add(zone_name_of_nameserver)
                    except ValueError:
                        pass
                    self._init_dict_key_with_an_empty_set_and_then_add(nameservers, nameserver, current_zone_name)

                print(f"Depends on zone: {current_zone_name}")
                zone_list.append(Zone(current_zone_name, current_zone_nameservers, current_zone_cnames))
        print(f"Dependencies recap: {len(zone_list)} zones, {len(self.cache.cache) - start_cache_length} cache entries added, {len(error_logs)} errors.\n")
        # TODO: togliere i Top-Level Domain
        return zone_list, zone_links, nameservers, error_logs

    def resolve_zone_of_nameserver(self, nameserver: str):
        subdomains = domain_name_utils.get_subdomains_name_list(nameserver, False)
        for domain in reversed(subdomains):
            try:
                rr = self.cache.lookup_first(domain, TypesRR.NS)
                return domain
            except NoRecordInCacheError:
                try:
                    rr_values, rr_aliases = self.do_query(domain, TypesRR.NS)
                    # self.cache.add_entry(rr_values)
                    return domain
                except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
                    pass
        raise ValueError

    def export_cache(self) -> None:
        """
        It exports the cache to a .csv file named 'cache.csv' in the output folder of the project root folder (PRD).

        """
        try:
            self.cache.write_to_csv_in_output_folder()
        except (PermissionError, FileNotFoundError, OSError):
            raise

    @classmethod
    def _split_domain_name_and_add_to_list(cls, _list: list, domain_name: str, root_included: bool) -> None:
        """
        It parse all the subdomains from a domain name, and appends (without duplicates) them in a list.

        :param _list: The list parameter where tuo put the subdomains.
        :type _list: list
        :param domain_name: The domain name from which all subdomains are extracted
        :type domain_name: str
        :param root_included: Flag to set if the root domain name should be considered or not.
        :type root_included: bool
        """
        split = domain_name_utils.get_subdomains_name_list(domain_name, root_included=root_included)
        for sub_domain in split:
            if sub_domain not in _list:
                _list.append(sub_domain)

    @classmethod
    def _split_domain_name_and_add_to_dict(cls, _dict: Dict[str, List[str]], key: str, domain_name: str, root_included: bool) -> None:
        split = domain_name_utils.get_subdomains_name_list(domain_name, root_included=root_included)
        for sub_domain in split:
            if sub_domain not in _dict[key]:
                _dict[key].append(sub_domain)

    @classmethod
    def _init_dict_key_with_an_empty_set(cls, _dict: dict, _key: any) -> None:
        try:
            _dict[_key]
        except KeyError:
            _dict[_key] = set()

    @classmethod
    def _init_dict_key_with_an_empty_set_and_then_add(cls, _dict: dict, _key: any, elem_to_add: any) -> None:
        try:
            _dict[_key]
        except KeyError:
            _dict[_key] = set()
        finally:
            _dict[_key].add(elem_to_add)
