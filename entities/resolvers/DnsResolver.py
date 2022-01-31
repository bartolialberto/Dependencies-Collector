import copy
from pathlib import Path
from typing import List, Tuple, Dict, Set
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

    # HIPOTHESIS USED:
    # - CNAME RR can have only one value
    # - Can't exist more than 1 CNAME RR with the same name
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
        """
        try:
            domain_name_utils.grammatically_correct(domain)
        except InvalidDomainNameError:
            raise
        """

        error_logs = list()
        start_cache_length = len(self.cache.cache)
        elaboration_domains = domain_name_utils.get_subdomains_name_list(domain, root_included=True, parameter_included=True)
        if len(elaboration_domains) == 0:
            raise InvalidDomainNameError(domain)  # giusto???
        zone_list = list()  # si va a popolare con ogni iterazione
        print(f"Cache has {start_cache_length} entries.")
        print(f"Looking at zone dependencies for: {domain} ..")
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
                zone, names_to_be_elaborated, error_logs_to_be_added = self.zone_check(names_path_param)
                for log in error_logs_to_be_added:
                    error_logs.append(log)
            except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
                error_logs.append(ErrorLog(e, current_domain, str(e)))
                continue

            for name in names_to_be_elaborated:
                list_utils.append_with_no_duplicates(elaboration_domains, name)

            list_utils.append_with_no_duplicates(zone_list, zone)

        zone_dependencies_per_nameserver, zone_dependencies_per_zone = self.extract_zone_name_dependencies(zone_list)
        direct_zone_name = self.extract_direct_zone_name(domain, zone_list)

        if not consider_tld:
            zone_list, zone_dependencies_per_zone, zone_dependencies_per_nameserver = self._remove_tld(self.tld_list, zone_list, zone_dependencies_per_zone, zone_dependencies_per_nameserver)

        print(
            f"Dependencies recap: {len(zone_list)} zones, {len(self.cache.cache) - start_cache_length} cache entries added, {len(error_logs)} errors.\n")

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

    # TODO
    def resolve_cname(self, cname: str, parameter_included=True) -> List[str]:
        try:
            names = self.__inner_resolve_cname(cname, None)
        except (DomainNonExistentError, UnknownReasonError):
            raise
        if len(names) == 1:     # only the parameter
            raise NoAvailablePathError(cname)
        else:
            if not parameter_included:
                names.remove(cname)
            return names

    def __inner_resolve_cname(self, cname: str, path: List[str] or None) -> List[str]:
        if path is None:
            path = list()
        else:
            pass
        path.append(cname)
        try:
            rr_answer = self.cache.lookup_first(cname, TypesRR.CNAME)
        except NoRecordInCacheError:
            try:
                rr_answer, rr_cnames = self.do_query(cname, TypesRR.CNAME)
                self.cache.add_entry(rr_answer)
            except NoAnswerError:
                return path
            except (DomainNonExistentError, UnknownReasonError):
                raise
        return self.__inner_resolve_cname(rr_answer.get_first_value(), path)

    def zone_check(self, domain_name_path: List[str]) -> Tuple[Zone, List[str], List[ErrorLog]]:
        domain_name = copy.deepcopy(domain_name_path[-1])
        error_logs_to_be_added = list()
        try:
            rr_answer, rr_cnames = self.cache.resolve_path(domain_name, TypesRR.NS, as_string=False)
            print(f"Depends on zone: {rr_answer.name}\t\t\t[NON-AUTHORITATIVE]")
        except NoAvailablePathError:
            try:
                rr_answer, rr_cnames = self.do_query(domain_name, TypesRR.NS)
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

    def parse_zone_dependencies_of_zone(self, current_zone: Zone, zone_list: List[Zone]) -> List[str]:
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
        subdomains = domain_name_utils.get_subdomains_name_list(name, root_included=True, parameter_included=False)
        result = list()
        for subdomain in subdomains:
            for zone in zone_list:
                if domain_name_utils.equals(subdomain, zone.name):
                    result.append(zone)
        return result

    def __parse_recursively_zones_of_name_server_from_zone_list(self, names_to_be_checked: List[str], zone_list: List[Zone], result: List[Zone] or None) -> List[Zone]:
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

    def try_to_resolve_partially_cached_access_path(self, name_server: str) -> Tuple[List[RRecord], RRecord, List[str]]:
        # case in which a name server was resolved previously, and now another name server is a domain name that has
        # as alias the previously quoted name server. So there's only the cname missing to complete the resolution.
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
        dn = domain_name_utils.insert_trailing_point(domain_name)
        for_zone_name_subdomains = reversed(domain_name_utils.get_subdomains_name_list(dn, root_included=True, parameter_included=True))
        zone_name_dependencies = list(map(lambda z: z.name, zone_list))
        for current_domain in for_zone_name_subdomains:
            if current_domain in zone_name_dependencies:
                return current_domain
        raise ValueError

    @classmethod
    def _remove_tld(cls, tld_list: List[str], zone_list: List[Zone], zone_dependencies_per_zone: Dict[str, List[str]], zone_dependencies_per_nameserver: Dict[str, List[str]]) -> Tuple[List[Zone], Dict[str, List[str]], Dict[str, List[str]]]:
        """
        This method removes TLDs from all data structures used as parameters.
        It needs also (as a parameter) a list of TLDs. The format of each TLD should be (example):
                com.

        :param tld_list: The list of TLDs.
        :type tld_list: List[str]
        :param zone_list: The Zone object list of dependency.
        :type zone_list: List[Zone]
        :param zone_dependencies_per_zone: The zone name dependencies per zone name dictionary.
        :type zone_dependencies_per_zone: Dict[str, List[str]]
        :param zone_dependencies_per_nameserver: The zone name dependencies per name server dictionary.
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

        # if zone_dependencies key contains only a tld as value, now that list of values is empty...
        # So key must be removed
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
