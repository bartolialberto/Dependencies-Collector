from pathlib import Path
from typing import List, Tuple, Dict
import dns.resolver
from dns.name import Name
from entities.LocalDnsResolverCache import LocalDnsResolverCache
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from entities.Zone import Zone
from entities.error_log.ErrorLog import ErrorLog
from entities.resolvers.results.DnsMailServersDependenciesResult import DnsMailServersDependenciesResult
from entities.resolvers.results.DnsZoneDependenciesResult import DnsZoneDependenciesResult
from entities.resolvers.results.MultipleDnsMailServerDependenciesResult import MultipleDnsMailServerDependenciesResult
from entities.resolvers.results.MultipleDnsZoneDependenciesResult import MultipleDnsZoneDependenciesResult
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoRecordInCacheError import NoRecordInCacheError
from exceptions.UnknownReasonError import UnknownReasonError
from utils import domain_name_utils, list_utils, email_address_utils


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
    tld_list : List[str] or None
        The list of Top-Level Domains to use when the application is executed with the intention of exclude them.
        The format of each tld is: no starting point only trailing point.
                example: com.
        It can be set to None to avoid any confrontation.
    """
    def __init__(self, tld_list: List[str] or None):
        """
        Instantiate this DnsResolver object.

        :param tld_list: A list of Top-Level Domains or None
        :type tld_list: List[str] or None
        """
        self.resolver = dns.resolver.Resolver()
        self.cache = LocalDnsResolverCache()
        self.tld_list = tld_list

    def do_query(self, name: str, type_rr: TypesRR) -> Tuple[RRecord, List[RRecord]]:
        """
        This method executes a real DNS query. It takes the domain name and the type as parameters.
        The result is a RR containing all the values in the values field, and a list of RRs of type CNAME containing (in
        the values field) all the aliases found in the resolving path. If the latter has no aliases then the list of
        aliases is empty.

        :param name: Name parameter.
        :type name: str
        :param type_rr: Type of the query.
        :type type_rr: TypesRR
        :raise DomainNonExistentError: If the name refers to a non existent domain.
        :raise NoAnswerError: If the query has no answer.
        :raise UnknownReasonError: If no non-broken nameservers are available to answer the question, or if the query
        name is too long after DNAME substitution.
        :return: A tuple containing the RR result and a list of RR containing the alias path.
        :rtype: Tuple[RRecord, List[RRecord]]
        """
        try:
            answer = self.resolver.resolve(name, type_rr.to_string())
            rr_aliases = list()
            final_name = None
            for cname in answer.chaining_result.cnames:
                for key in cname.items.keys():
                    name = str(cname.name)
                    alias_value = str(key.target)
                    rr_aliases.append(RRecord(name, TypesRR.CNAME, alias_value))
                    final_name = alias_value
            if final_name is None:
                final_name = name
            rr_values = list()
            for ad in answer:
                if isinstance(ad, Name):
                    rr_values.append(str(ad))
                else:
                    rr_values.append(ad.to_text())
            response_rrecord = RRecord(final_name, type_rr, rr_values)
            return response_rrecord, rr_aliases
        except dns.resolver.NXDOMAIN:  # name is a domain that does not exist
            raise DomainNonExistentError(name)
        except dns.resolver.NoAnswer:  # there is no answer
            raise NoAnswerError(name, type_rr)
        except (dns.resolver.NoNameservers, dns.resolver.YXDOMAIN) as e:
            raise UnknownReasonError(message=str(e))
        except Exception as e:  # fail because of another reason...
            raise UnknownReasonError(message=str(e))

    def resolve_multiple_domains_dependencies(self, domain_list: List[str], reset_cache_per_elaboration=False, consider_tld=True) -> MultipleDnsZoneDependenciesResult:
        """
        This method resolves the zone dependencies of multiple domain names.
        If something goes wrong, exceptions are not raised but the error_logs of the result will be populated with what
        went wrong.

        :param domain_list: A list of domain names.
        :type domain_list: List[str]
        :param reset_cache_per_elaboration: Flag that indicates if cache should be cleared after each domain name
        resolving. Useful only for testing.
        :type reset_cache_per_elaboration: bool
        :param consider_tld: Flag that indicates if Top-Level Domains should be considered.
        :type consider_tld: bool
        :return: A MultipleDnsZoneDependenciesResult object.
        :rtype: MultipleDnsZoneDependenciesResult
        """
        final_results = MultipleDnsZoneDependenciesResult()
        for domain in domain_list:
            try:
                if reset_cache_per_elaboration:
                    self.cache.clear()
                resolver_result = self.resolve_domain_dependencies(domain, consider_tld=consider_tld)
                final_results.merge_single_resolver_result(domain, resolver_result)
            except InvalidDomainNameError as e:
                final_results.error_logs.append(ErrorLog(e, domain, str(e)))

        return final_results

    def resolve_multiple_mail_domains(self, mail_domains: List[str]) -> MultipleDnsMailServerDependenciesResult:
        """
        This method resolves the mail servers dependencies of multiple mail domains.
        If something goes wrong, exceptions are not raised but the error_logs of the result will be populated with what
        went wrong.

        :param mail_domains: A list of mail domains.
        :param mail_domains: List[str]
        :return: A MultipleDnsMailServerDependenciesResult object.
        :rtype: MultipleDnsMailServerDependenciesResult
        """
        final_results = MultipleDnsMailServerDependenciesResult()
        for mail_domain in mail_domains:
            print(f"Resolving mail domain: {mail_domain}")
            try:
                resolver_result = self.resolve_mail_domain(mail_domain)
                final_results.add_dependency(mail_domain, resolver_result)
            except (InvalidDomainNameError, NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
                print(f"!!! {str(e)} !!!")
                final_results.append_error_log(ErrorLog(e, mail_domain, str(e)))
            print()
        return final_results

    def resolve_mail_domain(self, mail_domain: str) -> DnsMailServersDependenciesResult:
        """
        This method resolves the mail servers dependencies of a mail domain.

        :param mail_domain: A mail domain.
        :type mail_domain: str
        :raise InvalidDomainNameError: If mail domain is not a well-formatted domain name or email address.
        :raise DomainNonExistentError: If query response says that name is a non-existent domain.
        :raise NoAnswerError: If query has no response.
        :raise UnknownReasonError: If query execution went wrong.
        :return: A DnsMailServersDependenciesResult object.
        :rtype: DnsMailServersDependenciesResult
        """
        try:
            domain_name_utils.grammatically_correct(mail_domain)
        except InvalidDomainNameError:
            try:
                email_address_utils.grammatically_correct(mail_domain)
            except InvalidDomainNameError as e:
                print(f"!!! {str(e)} !!!")
                raise
        result = DnsMailServersDependenciesResult()
        try:
            mx_values, mx_aliases = self.do_query(mail_domain, TypesRR.MX)
        except (DomainNonExistentError, NoAnswerError, UnknownReasonError) as e:
            print(f"!!! {str(e)} !!!")
            raise
        for i, value in enumerate(mx_values.values):
            print(f"mail server[{i+1}/{len(mx_values.values)}]: {RRecord.parse_mail_server_from_value(value)}")
            result.add_mail_server(RRecord.parse_mail_server_from_value(value))
        return result

    def resolve_domain_dependencies(self, domain: str, consider_tld=True) -> DnsZoneDependenciesResult:
        """
        This method resolves the zone dependencies of a domain name.

        :param domain: A domain name.
        :type domain: str
        :param consider_tld: Flag that indicates if Top-Level Domains should be considered.
        :type consider_tld: bool
        :raise InvalidDomainNameError: If domain name parameter is not a well-formatted domain name.
        :return: A DnsZoneDependenciesResult object.
        :rtype: DnsZoneDependenciesResult
        """
        try:
            domain_name_utils.grammatically_correct(domain)
        except InvalidDomainNameError:
            raise

        #
        zone_dependencies_per_zone = dict()
        zone_dependencies_per_nameserver = dict()
        error_logs = list()
        start_cache_length = len(self.cache.cache)
        elaboration_domains = domain_name_utils.get_subdomains_name_list(domain, root_included=True)
        if len(elaboration_domains) == 0:
            raise InvalidDomainNameError(domain)  # giusto???
        zone_list = list()  # si va a popolare con ogni iterazione
        print(f"Cache has {start_cache_length} entries.")
        print(f"Looking at zone dependencies for '{domain}'..")
        for current_domain in elaboration_domains:
            # reset all variables for new iteration
            current_zone_nameservers = list()
            current_zone_cnames = list()
            current_zone_addresses = list()
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
                    self._split_domain_name_and_add_to_list(elaboration_domains, alias, root_included=False)
                zone_names = self.cache.resolve_zones_from_nameserver(current_domain)
                for zone_name in zone_names:
                    tmp = list(map(lambda z: z.name, zone_list))
                    if zone_name not in tmp:
                        zone = self.cache.resolve_zone_from_zone_name(zone_name)
                        zone_list.append(zone)
                        print(f"Depends on zone: {zone.name}\t\t\t[NON-AUTHORITATIVE]")
                        for nm in zone.nameservers:
                            self._split_domain_name_and_add_to_list(elaboration_domains, nm, False)
            except (NoRecordInCacheError, NoAvailablePathError):
                try:
                    rr_cname_answer, rr_cname_aliases = self.do_query(current_domain, TypesRR.CNAME)
                    self.cache.add_entry(rr_cname_answer)
                    for rr in rr_cname_aliases:
                        self.cache.add_entry(rr)
                    self._split_domain_name_and_add_to_list(elaboration_domains, rr_cname_answer.get_first_value(), root_included=False)
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
                    pass
                except (DomainNonExistentError, UnknownReasonError) as e:
                    error_logs.append(ErrorLog(e, current_domain, str(e)))

            # is domain a zone name?
            try:
                rr_ns = self.cache.lookup_first(current_domain, TypesRR.NS)
                zone = self.cache.resolve_zone_from_ns_rr(rr_ns)  # raise NoRecordInCacheError too
                current_zone_name = zone.name
                current_zone_nameservers = zone.nameservers
                current_zone_cnames = zone.aliases
                current_zone_addresses = zone.addresses

                #
                self._init_dict_key_with_an_empty_set(zone_dependencies_per_zone, current_domain)

                for nameserver in current_zone_nameservers:
                    self._split_domain_name_and_add_to_list(elaboration_domains, nameserver, False)

                    #
                    try:
                        zone_name_of_nameserver = self.resolve_zone_of_nameserver(nameserver)
                        zone_dependencies_per_zone[current_domain].add(zone_name_of_nameserver)
                    except ValueError:
                        pass
                    self._init_dict_key_with_an_empty_set_and_then_add(zone_dependencies_per_nameserver, nameserver, current_zone_name)

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
                self._init_dict_key_with_an_empty_set(zone_dependencies_per_zone, current_domain)

                # no rr_aliases poiché una query NS non può avere alias
                for nameserver in rr_ns_answer.values:
                    # per ogni nameserver devo considerare che potrebbero esserci già dei RR di tipo A ed il nameserver
                    # corrente è solo un alias di uno di quei nameserver che ha già (appunto) rr di tipo A nella cache,
                    # quindi in verità è già risolto (==> non server metterlo in cache, sennò ho doppioni)
                    try:
                        rr_a, rr_cnames = self.cache.resolve_path(nameserver, as_string=False)
                        list_utils.append_with_no_duplicates(current_zone_nameservers, nameserver)  # ma se il RR ha solo il campo values diverso?
                        for rr_cname in rr_cnames:
                            list_utils.append_with_no_duplicates(current_zone_cnames, rr_cname)
                        list_utils.append_with_no_duplicates(current_zone_addresses, rr_a)
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
                            list_utils.append_with_no_duplicates(current_zone_nameservers, nameserver)  # ma se il RR ha solo il campo values diverso?
                            list_utils.append_with_no_duplicates(current_zone_addresses, rr_a_answer)
                        except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as exc:
                            error_logs.append(ErrorLog(exc, current_domain, str(exc)))
                    self._split_domain_name_and_add_to_list(elaboration_domains, nameserver, False)

                    #
                    try:
                        zone_name_of_nameserver = self.resolve_zone_of_nameserver(nameserver)
                        zone_dependencies_per_zone[current_domain].add(zone_name_of_nameserver)
                    except ValueError:
                        pass
                    self._init_dict_key_with_an_empty_set_and_then_add(zone_dependencies_per_nameserver, nameserver, current_zone_name)

                print(f"Depends on zone: {current_zone_name}")
                zone_list.append(Zone(current_zone_name, current_zone_nameservers, current_zone_cnames, current_zone_addresses))
        print(f"Dependencies recap: {len(zone_list)} zones, {len(self.cache.cache) - start_cache_length} cache entries added, {len(error_logs)} errors.\n")

        dn = domain_name_utils.insert_trailing_point(domain)
        for_zone_name_subdomains = reversed(domain_name_utils.get_subdomains_name_list(dn, root_included=True))
        zone_name_dependencies = list(map(lambda z: z.name, zone_list))
        direct_zone_name = None
        for current_domain in for_zone_name_subdomains:
            if current_domain in zone_name_dependencies:
                direct_zone_name = current_domain
                break

        if not consider_tld:
            zone_list, zone_dependencies_per_zone, zone_dependencies_per_nameserver = self._remove_tld(self.tld_list, zone_list, zone_dependencies_per_zone, zone_dependencies_per_nameserver)
        return DnsZoneDependenciesResult(zone_list, direct_zone_name, zone_dependencies_per_zone, zone_dependencies_per_nameserver, error_logs)

    def resolve_web_site_domain_name(self, web_site_domain_name: str) -> Tuple[RRecord, List[RRecord]]:
        # TODO: docs
        try:
            rr_a, rr_cnames = self.cache.resolve_path(web_site_domain_name, as_string=False)
        except NoAvailablePathError:
            try:
                rr_a, rr_cnames = self.do_query(web_site_domain_name, TypesRR.A)
                self.cache.add_entry(rr_a)
                for rr in rr_cnames:
                    self.cache.add_entry(rr)
            except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
                raise        # TODO
        return rr_a, rr_cnames

    # TODO: refactor
    def resolve_zone_of_nameserver(self, nameserver: str):
        subdomains = domain_name_utils.get_subdomains_name_list(nameserver, False)
        for domain in reversed(subdomains):
            try:
                rr = self.cache.lookup_first(domain, TypesRR.NS)
                return domain
            except NoRecordInCacheError:
                try:
                    rr_values, rr_aliases = self.do_query(domain, TypesRR.NS)
                    return domain
                except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
                    pass
        raise ValueError

    def export_cache(self, filename="dns_cache", project_root_directory=Path.cwd()) -> None:
        """
        It exports the cache to a .csv file named 'dns_cache' in the output folder of the project root folder (PRD).

        :param filename: The personalized filename without extension, default is 'dns_cache'.
        :type filename: str
        :param project_root_directory: The Path object pointing at the project root directory.
        :type project_root_directory: Path
        :raise PermissionError: If filepath points to a directory.
        :raise FileNotFoundError: If it is impossible to open the file.
        :raise OSError: If a general I/O error occurs.
        """
        try:
            self.cache.write_to_csv_in_output_folder(filename=filename, project_root_directory=project_root_directory)
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

    @classmethod
    def _remove_tld(cls, tld_list: List[str], zone_list: List[Zone], zone_dependencies_per_zone: Dict[str, List[str]], zone_dependencies_per_nameserver: Dict[str, List[str]]) -> Tuple[List[Zone], Dict[str, List[str]], Dict[str, List[str]]]:
        """
        This method removes TLDs from all data structures used as parameters.
        It needs also (as a parameter) a list of TLDs. The format of each TLD should be:
                example: com.

        :param tld_list:
        :type tld_list: List[str]
        :param zone_list:
        :type zone_list: List[Zone]
        :param zone_dependencies_per_zone:
        :type zone_dependencies_per_zone: Dict[str, List[str]]
        :param zone_dependencies_per_nameserver:
        :type zone_dependencies_per_nameserver: Dict[str, List[str]]
        :return: All the parameters 'filtered' from TLDs as a tuple.
        :rtype: Tuple[List[Zone], Dict[str, List[str]], Dict[str, List[str]]]
        """
        filtered_zone_list = list(filter(lambda z: z.name not in tld_list, zone_list))

        filtered_zone_dependencies_per_zone = dict()
        for zone_name in zone_dependencies_per_zone.keys():
            if zone_name not in tld_list:
                filtered_zone_dependencies_per_zone[zone_name] = list()
        for zone_name, list_zone_names in filtered_zone_dependencies_per_zone.items():
            for zn in zone_dependencies_per_zone[zone_name]:
                if zn not in tld_list:
                    filtered_zone_dependencies_per_zone[zone_name].append(zn)

        filtered_zone_dependencies_per_nameserver = dict()
        for nameserver in zone_dependencies_per_nameserver.keys():
            if nameserver not in tld_list:
                filtered_zone_dependencies_per_nameserver[nameserver] = list()
        for nameserver, list_zone_names in filtered_zone_dependencies_per_nameserver.items():
            for zn in zone_dependencies_per_nameserver[nameserver]:
                if zn not in tld_list:
                    filtered_zone_dependencies_per_nameserver[nameserver].append(zn)

        # if zone_dependencies key contains only a tld as value, now that list of values is empty... So key must be removed
        keys_to_be_removed = set()
        for zone_name in filtered_zone_dependencies_per_zone.keys():
            if len(filtered_zone_dependencies_per_zone[zone_name]) == 0:
                keys_to_be_removed.add(zone_name)
        for key in keys_to_be_removed:
            filtered_zone_dependencies_per_zone.pop(key)
        keys_to_be_removed = set()
        for nameserver in filtered_zone_dependencies_per_nameserver.keys():
            if len(filtered_zone_dependencies_per_nameserver[nameserver]) == 0:
                keys_to_be_removed.add(nameserver)
        for key in keys_to_be_removed:
            filtered_zone_dependencies_per_nameserver.pop(key)
        return filtered_zone_list, filtered_zone_dependencies_per_zone, filtered_zone_dependencies_per_nameserver
