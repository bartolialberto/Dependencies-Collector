import copy
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
from exceptions.NotWantedTLDError import NotWantedTLDError
from exceptions.UnknownReasonError import UnknownReasonError
from utils import domain_name_utils, list_utils


class DnsResolver:
    """
    This class represents a simple DNS resolver for the application. Is based on a real and complete DNS resolver from
    the 'dnspython' module.

    ...

    Attributes
    ----------
    resolver : DnsResolver
        The real and complete DNS resolver from the dnspython module.
    cache : LocalDnsResolverCache
        The cache used to handle requests.
    consider_tld : bool
        Flag that tells if the resolver has to consider TLDs. This means that when a TLD is encountered in the
        elaboration, it is avoided and from the its name servers it is not deducted any other domain name to elaborate.
    """
    def __init__(self, consider_tld: bool):
        """
        Instantiate this DnsResolver object.

        :param consider_tld: Flag that tells if the resolver has to consider TLDs.
        :type consider_tld: bool
        """
        self.resolver = dns.resolver.Resolver()
        self.cache = LocalDnsResolverCache()
        self.consider_tld = consider_tld

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

    def resolve_multiple_domains_dependencies(self, domain_list: List[str], reset_cache_per_elaboration=False) -> MultipleDnsZoneDependenciesResult:
        """
        This method resolves the zone dependencies of multiple domain names.
        If something goes wrong, exceptions are not raised but the error_logs of the result will be populated with what
        went wrong.

        :param domain_list: A list of domain names.
        :type domain_list: List[str]
        :param reset_cache_per_elaboration: Flag that indicates if cache should be cleared after each domain name
        resolving. Useful only for testing.
        :type reset_cache_per_elaboration: bool
        :return: A MultipleDnsZoneDependenciesResult object.
        :rtype: MultipleDnsZoneDependenciesResult
        """
        final_results = MultipleDnsZoneDependenciesResult()
        for i, domain in enumerate(domain_list):
            try:
                if reset_cache_per_elaboration:
                    self.cache.clear()
                print(f"Looking at zone dependencies for domain[{i+1}/{len(domain_list)}]: {domain} ..")
                resolver_result = self.resolve_domain_dependencies(domain)
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
        for i, mail_domain in enumerate(mail_domains):
            print(f"Resolving mail domain[{i+1}/{len(mail_domains)}]: {mail_domain}")
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

    def resolve_domain_dependencies(self, domain: str) -> DnsZoneDependenciesResult:
        """
        This method resolves the zone dependencies of a domain name.

        :param domain: A domain name.
        :type domain: str
        :raise InvalidDomainNameError: If domain name parameter is not a well-formatted domain name.
        :return: A DnsZoneDependenciesResult object.
        :rtype: DnsZoneDependenciesResult
        """
        error_logs = list()
        start_cache_length = len(self.cache.cache)
        elaboration_domains = domain_name_utils.get_subdomains_name_list(domain, root_included=True, parameter_included=True)
        if len(elaboration_domains) == 0:
            raise InvalidDomainNameError(domain)  # giusto???
        zone_list = list()  # si va a popolare con ogni iterazione
        print(f"Cache has {start_cache_length} entries.")
        for current_domain in elaboration_domains:
            # is domain a nameserver with aliases?
            try:
                names_path_param = self.resolve_cname(current_domain, parameter_included=True)
                names_path = copy.deepcopy(names_path_param)
                try:
                    names_path.remove(current_domain)
                except ValueError:
                    pass
                for name in names_path:
                    name_subdomains = domain_name_utils.get_subdomains_name_list(name, root_included=False, parameter_included=False)
                    for name_subdomain in name_subdomains:
                        list_utils.append_with_no_duplicates(elaboration_domains, name_subdomain)
                current_domain = names_path[-1]
            except NoAvailablePathError:
                names_path_param = [current_domain]
                pass
            except (DomainNonExistentError, UnknownReasonError) as e:
                error_logs.append(ErrorLog(e, current_domain, str(e)))
                names_path_param = [current_domain]

            try:
                zone, names_to_be_elaborated, error_logs_to_be_added = self.resolve_zone(names_path_param)
                for log in error_logs_to_be_added:
                    error_logs.append(log)
            except NotWantedTLDError:
                continue
            except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
                error_logs.append(ErrorLog(e, current_domain, str(e)))
                continue

            for name in names_to_be_elaborated:
                list_utils.append_with_no_duplicates(elaboration_domains, name)

            list_utils.append_with_no_duplicates(zone_list, zone)

        zone_dependencies_per_nameserver, zone_dependencies_per_zone = self.extract_zone_name_dependencies(zone_list)
        try:
            direct_zone_name = self.extract_direct_zone_name(domain, zone_list)
        except ValueError:
            direct_zone_name = None
        print(f"Dependencies recap: {len(zone_list)} zones, {len(self.cache.cache) - start_cache_length} cache entries added, {len(error_logs)} errors.\n")
        return DnsZoneDependenciesResult(zone_list, direct_zone_name, zone_dependencies_per_zone, zone_dependencies_per_nameserver, error_logs)

    def resolve_web_site_domain_name(self, web_site_domain_name: str) -> Tuple[RRecord, List[RRecord]]:
        """
        This method resolves the domain name parameter (supposed to be extracted from an URL) in all the alias to
        follow before the IP address is resolved.

        :param web_site_domain_name: A domain name.
        :type web_site_domain_name: str
        :return: A tuple containing first the A type RR answer, and then a list of CNAME type RR that represents the
        access path.
        :rtype: Tuple[RRecord, List[RRecord]]
        """
        try:
            rr_a, rr_cnames = self.cache.resolve_path(web_site_domain_name, TypesRR.A, as_string=False)
        except NoAvailablePathError:
            try:
                rr_a, rr_cnames = self.do_query(web_site_domain_name, TypesRR.A)
                self.cache.add_entry(rr_a, control_for_no_duplicates=True)
                self.cache.add_entries(rr_cnames, control_for_no_duplicates=True)
            except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
                raise
        return rr_a, rr_cnames

    def resolve_cname(self, name: str, parameter_included=True) -> List[str]:
        """
        This methods resolves the CNAME RR of the name parameter, then if there are more CNAME RR from the alias of the
        previous CNAME RR then recursively it will continue the resolving. It will stops when there are no other CNAME
        RR available for the last alias computed.
        In the end it will be created a sort of 'alias path'.

        :param name: A domain name.
        :type name: str
        :param parameter_included: Decide if in the result list the parameter should be considered.
        :type parameter_included: bool
        :raise DomainNonExistentError: If during the CNAME query happens such error.
        :raise UnknownReasonError: If during the CNAME query happens such error.
        :raise NoAvailablePathError: If there's no path for name parameter.
        :return: The path of alias.
        :rtype: List[str]
        """
        try:
            names = self.__inner_resolve_cname(name, None)
        except (DomainNonExistentError, UnknownReasonError):
            raise
        if len(names) == 1:     # only the parameter
            raise NoAvailablePathError(name)
        else:
            if not parameter_included:
                names.remove(name)
            return names

    def __inner_resolve_cname(self, name: str, path: List[str] or None) -> List[str]:
        """
        Recursive auxiliary method in 'resolve_cname' method.

        :param name: A domain name.
        :type name: str
        :param path: Result carried through all recursive invocations. None value corresponds to the initial seed.
        :type path: List[str] or None
        :raise DomainNonExistentError: If during the CNAME query happens such error.
        :raise UnknownReasonError: If during the CNAME query happens such error.
        :return: The path of alias.
        :rtype: List[str]
        """
        if path is None:
            path = list()
        else:
            pass
        path.append(name)
        try:
            rr_answer = self.cache.lookup_first(name, TypesRR.CNAME)
        except NoRecordInCacheError:
            try:
                rr_answer, rr_cnames = self.do_query(name, TypesRR.CNAME)
                self.cache.add_entry(rr_answer)
            except NoAnswerError:
                return path
            except (DomainNonExistentError, UnknownReasonError):
                raise
        return self.__inner_resolve_cname(rr_answer.get_first_value(), path)

    def resolve_zone(self, domain_name_path: List[str]) -> Tuple[Zone, List[str], List[ErrorLog]]:
        """
        This method resolves the NS RR of the domain name in the domain_name_path parameter. It will return the zone
        (as Zone, the application-defined object) resolved, a list of name to append in the current domain name
        elaboration list to be done and a list of error logs happened during the method execution.

        :param domain_name_path: The path resolved from the CNAME previous resolving.
        :type domain_name_path: List[str]
        :raise DomainNonExistentError: If during the NS query happens such error.
        :raise UnknownReasonError: If during the NS query happens such error.
        :raise NoAnswerError: If during the NS query happens such error.
        :return: A tuple containing the zone resolved, the names to be added to continue the zone dependencies resolving
        and a list of error logs.
        :rtype: Tuple[Zone, List[str], List[ErrorLog]]
        """
        domain_name = copy.deepcopy(domain_name_path[-1])
        error_logs_to_be_added = list()
        try:
            rr_answer = self.cache.lookup_first(domain_name, TypesRR.NS)
            if self.consider_tld == False and domain_name_utils.is_tld(domain_name):
                raise NotWantedTLDError
            print(f"Depends on zone: {rr_answer.name}\t\t\t[NON-AUTHORITATIVE]")
        except NoRecordInCacheError:
            try:
                rr_answer, rr_cnames = self.do_query(domain_name, TypesRR.NS)
                if self.consider_tld == False and domain_name_utils.is_tld(domain_name):
                    raise NotWantedTLDError
                print(f"Depends on zone: {rr_answer.name}")
                self.cache.add_entry(rr_answer)
                self.cache.add_entries(rr_cnames)
            except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
                raise

        try:
            rr_cnames = RRecord.construct_cname_rrs_from_list_access_path(domain_name_path)
        except ValueError:
            rr_cnames = list()

        names_to_be_elaborated = list()
        tmp = list(map(lambda r: r.name, rr_cnames))
        for name in tmp:
            sub_names = domain_name_utils.get_subdomains_name_list(name, root_included=False, parameter_included=False)
            for sub_name in sub_names:
                names_to_be_elaborated.append(sub_name)

        zone_name = rr_answer.name
        zone_name_servers = list()
        zone_rr_name_servers_aliases = list()
        zone_rr_zone_name_aliases = copy.deepcopy(rr_cnames)
        zone_rr_addresses = list()
        for name_server in rr_answer.values:
            zone_name_servers.append(name_server)
            name_server_subdomains = domain_name_utils.get_subdomains_name_list(name_server, root_included=False, parameter_included=False)
            for name_server_subdomain in name_server_subdomains:
                list_utils.append_with_no_duplicates(names_to_be_elaborated, name_server_subdomain)
            try:
                nameserver_rr_answer, nameserver_rr_cnames = self.cache.resolve_path(name_server, TypesRR.A, as_string=False)
            except NoAvailablePathError:
                # attempt for partially resolved path in cache
                try:
                    rr_aliases_to_be_added, alias_rr_answer, alias_subdomains = self.try_to_resolve_partially_cached_access_path(name_server)
                    for rr in rr_aliases_to_be_added:
                        zone_rr_name_servers_aliases.append(rr)
                    zone_rr_addresses.append(alias_rr_answer)
                    for subdomain in alias_subdomains:
                        list_utils.append_with_no_duplicates(names_to_be_elaborated, subdomain)
                    continue
                except (DomainNonExistentError, UnknownReasonError) as e:
                    error_logs_to_be_added.append(ErrorLog(e, name_server, str(e)))
                except (NoAnswerError, NoAvailablePathError):
                    pass
                # normal elaboration
                try:
                    nameserver_rr_answer, nameserver_rr_cnames = self.do_query(name_server, TypesRR.A)
                    self.cache.add_entry(nameserver_rr_answer)
                    self.cache.add_entries(nameserver_rr_cnames)
                except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
                    error_logs_to_be_added.append(ErrorLog(e, name_server, str(e)))
                    continue
            for rr in nameserver_rr_cnames:
                zone_rr_name_servers_aliases.append(rr)
            zone_rr_addresses.append(nameserver_rr_answer)
        zone = Zone(zone_name, zone_name_servers, zone_rr_name_servers_aliases, zone_rr_addresses, zone_rr_zone_name_aliases)
        return zone, names_to_be_elaborated, error_logs_to_be_added

    def extract_zone_name_dependencies(self, zone_list: List[Zone]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        """
        This method extracts the zone dependencies for each name server and the zone dependencies for each zone name
        from the Zone (the application-defined object) list resolved.

        :param zone_list:
        :type zone_list: List[Zone]
        :return: A dictionary that associates all the name server to a list of zone names and then a dictionary that
        associates all zone names to a list of zone names, as a tuple.
        :rtype: Tuple[Dict[str, List[str]], Dict[str, List[str]]]
        """
        zone_name_dependencies_per_zone_name = dict()
        zone_name_dependencies_per_name_server = dict()
        for zone in zone_list:
            # resolve zone dependency of zone
            try:
                zone_name_dependencies_per_zone_name[zone.name]
            except KeyError:
                zone_name_dependencies_per_zone_name[zone.name] = list()
            zone_names = self.parse_zone_dependencies_of_zone(zone, zone_list)
            for zone_name in zone_names:
                list_utils.append_with_no_duplicates(zone_name_dependencies_per_zone_name[zone.name], zone_name)

            # resolve zone dependency of name server
            for name_server in zone.nameservers:
                try:
                    zone_name_dependencies_per_name_server[name_server]
                except KeyError:
                    zone_name_dependencies_per_name_server[name_server] = list()
                list_utils.append_with_no_duplicates(zone_name_dependencies_per_name_server[name_server], zone.name)        # no duplicates cause name servers can be of more zones
                zone_names = self.parse_zone_dependencies_of_name_server(name_server, zone_list)
                for zone_name in zone_names:
                    list_utils.append_with_no_duplicates(zone_name_dependencies_per_name_server[name_server], zone_name)
        # eliminate the self zone from its dependencies
        for zone in zone_list:
            try:
                zone_name_dependencies_per_zone_name[zone.name].remove(zone.name)
            except ValueError:
                pass
        return zone_name_dependencies_per_name_server, zone_name_dependencies_per_zone_name

    def parse_zone_dependencies_of_name_server(self, name_server: str, zone_list: List[Zone]) -> List[str]:
        """
        This methods takes as data pool the Zone (the application-defined object) list resolved and extract the zone
        dependencies from the name_server parameter.

        :param name_server: A name server.
        :type name_server: str
        :param zone_list: All the Zone (the application-defined object) list resolved.
        :type zone_list: List[Zone]
        :return: A list of zone names.
        :rtype: List[str]
        """
        zone_dependencies = list()
        # ancestor zones
        zones = self.__parse_zones_of_domain_name_from_zone_list(name_server, zone_list)
        for zone in zones:
            zone_dependencies.append(zone)
        # zones from name servers
        for zone in zones:
            copy_name_servers = copy.deepcopy(zone.nameservers)
            zs = self.__parse_recursively_zones_of_name_server_from_zone_list(copy_name_servers, zone_list, None)
            for z in zs:
                list_utils.append_with_no_duplicates(zone_dependencies, z)
                list_utils.append_with_no_duplicates(zones, z)
        return list(map(lambda zo: zo.name, zone_dependencies))

    def __parse_recursively_zones_of_name_server_from_zone_list(self, names_to_be_checked: List[str], zone_list: List[Zone], result: List[Zone] or None) -> List[Zone]:
        """
        Recursive auxiliary method used in 'parse_zone_dependencies_of_name_server' method.

        :param names_to_be_checked: The name to check carried through all recursive invocations.
        :type names_to_be_checked: List[str]
        :param zone_list: All the Zone (the application-defined object) list resolved.
        :type zone_list: List[Zone]
        :param result: Result carried through all recursive invocations. None value corresponds to the initial seed.
        :type result: List[Zone] or None
        :return: A list of Zone (the application-defined object).
        :rtype: List[Zone]
        """
        if result is None:
            result = list()
        else:
            pass
        if len(names_to_be_checked) == 0:
            return result
        start_names_to_be_checked = copy.deepcopy(names_to_be_checked)
        for name in names_to_be_checked:
            try:
                rr_answer, rr_cnames = self.cache.resolve_path(name, TypesRR.A, as_string=False)
                for rr in rr_cnames:
                    list_utils.append_with_no_duplicates(names_to_be_checked, rr.name)
                list_utils.append_with_no_duplicates(names_to_be_checked, rr_answer.name)
            except NoAvailablePathError:
                pass
            zones = self.__parse_zones_of_domain_name_from_zone_list(name, zone_list)
            for zone in zones:
                list_utils.append_with_no_duplicates(result, zone)
        for name in start_names_to_be_checked:
            names_to_be_checked.remove(name)
        return self.__parse_recursively_zones_of_name_server_from_zone_list(names_to_be_checked, zone_list, result)

    def parse_zone_dependencies_of_zone(self, current_zone: Zone, zone_list: List[Zone]) -> List[str]:
        """
        This methods takes as data pool the Zone (the application-defined object) list resolved and extract the zone
        dependencies from the current_zone parameter.

        :param current_zone: A Zone (the application-defined object) object.
        :type current_zone: Zone
        :param zone_list: All the Zone (the application-defined object) list resolved.
        :type zone_list: List[Zone]
        :return: A list of zone names.
        :rtype: List[str]
        """
        zone_dependencies = list()
        # ancestor zones
        zones = self.__parse_zones_of_domain_name_from_zone_list(current_zone.name, zone_list)
        for zone in zones:
            zone_dependencies.append(zone)
        # zones from name servers
        for name_server in current_zone.nameservers:
            name_server_zones = self.__parse_zones_of_domain_name_from_zone_list(name_server, zone_list)
            for z in name_server_zones:
                list_utils.append_with_no_duplicates(zone_dependencies, z)
        return list(map(lambda zo: zo.name, zone_dependencies))

    def __parse_zones_of_domain_name_from_zone_list(self, name: str, zone_list: List[Zone]) -> List[Zone]:
        """
        This methods takes as data pool the Zone (the application-defined object) list resolved.
        Then it creates a list of domain names from the name parameter considering all the ancestor domain names and
        extract the zone dependencies from the data pool mentioned above.

        :param name: name
        :type name: str
        :param zone_list: The Zone (the application-defined object) list used as data pool.
        :type zone_list: List[Zone]
        :return: A list of Zone (the application-defined object).
        :rtype: List[Zone]
        """
        subdomains = domain_name_utils.get_subdomains_name_list(name, root_included=True, parameter_included=False)
        result = list()
        for subdomain in subdomains:
            for zone in zone_list:
                if domain_name_utils.equals(subdomain, zone.name):
                    result.append(zone)
        return result

    def try_to_resolve_partially_cached_access_path(self, name_server: str) -> Tuple[List[RRecord], RRecord, List[str]]:
        """
        This method is used in the scenario where a certain domain name access path is already resolved in the cache,
        and the name_server parameter (domain name yet to compute) has a CNAME RR associated to the previous mentioned
        domain name.
        It returns the entire CNAME RRs followed to resolve the access path, the A RR that resolves the access path and
        the domain names to be added in the current domain names elaboration, all as a tuple.

        :param name_server: A domain name.
        :type name_server: str
        :raise NoAnswerError: If the CNAME query raises such error.
        :raise DomainNonExistentError: If the CNAME query raises such error.
        :raise UnknownReasonError: If the CNAME query raises such error.
        :raise NoAvailablePathError: If the A RR is not contained in cache.
        :return: The entire CNAME RRs followed to resolve the access path, the A RR that resolves the access path and
        the domain names to be added in the current domain names elaboration, all as a tuple.
        :rtype: Tuple[List[RRecord], RRecord, List[str]]
        """
        try:
            rr_answer, rr_cnames = self.do_query(name_server, TypesRR.CNAME)
        except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
            raise
        self.cache.add_entry(rr_answer)
        alias = rr_answer.get_first_value()
        alias_subdomains = domain_name_utils.get_subdomains_name_list(alias, root_included=False, parameter_included=False)
        rr_aliases_to_be_added = list()
        rr_aliases_to_be_added.append(rr_answer)
        try:
            alias_rr_answer, alias_rr_cnames = self.cache.resolve_path(alias, TypesRR.A)
        except NoAvailablePathError:
            raise
        for rr in alias_rr_cnames:
            rr_aliases_to_be_added.append(rr)
        return rr_aliases_to_be_added, alias_rr_answer, alias_subdomains

    def extract_direct_zone_name(self, domain_name: str, zone_list: List[Zone]) -> str:
        """
        This method extracts the direct zone of the domain name parameter from the zone_list parameter used as data
        pool.

        :param domain_name: A domain name.
        :type domain_name: str
        :param zone_list: All the Zone (the application-defined object) list resolved.
        :type zone_list: List[Zone]
        :raise ValueError: If there's no match from all the ancestor domain name as zone. Should never happen..
        :return: The direct zone name.
        :rtype: str
        """
        dn = domain_name_utils.insert_trailing_point(domain_name)
        for_zone_name_subdomains = reversed(domain_name_utils.get_subdomains_name_list(dn, root_included=True, parameter_included=True))
        zone_name_dependencies = list(map(lambda z: z.name, zone_list))
        for current_domain in for_zone_name_subdomains:
            if current_domain in zone_name_dependencies:
                return current_domain
        raise ValueError
