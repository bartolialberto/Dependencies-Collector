from typing import List, Tuple, Dict, Set
import dns.resolver
from dns.name import Name
from entities.DomainName import DomainName
from entities.LocalDnsResolverCache import LocalDnsResolverCache
from entities.paths.APath import APath
from entities.paths.CNAMEChain import CNAMEPath
from entities.paths.Path import Path
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR
from entities.Zone import Zone
from entities.error_log.ErrorLog import ErrorLog
from entities.paths.builders.APathBuilder import APathBuilder
from entities.paths.builders.CNAMEPathBuilder import CNAMEPathBuilder
from entities.paths.builders.MXPathBuilder import MXPathBuilder
from entities.paths.builders.NSPathBuilder import NSPathBuilder
from entities.resolvers.results.MailDomainResolvingResult import MailDomainResolvingResult
from entities.resolvers.results.DnsZoneDependenciesResult import DnsZoneDependenciesResult
from entities.resolvers.results.MultipleMailDomainResolvingResult import MultipleMailDomainResolvingResult
from entities.resolvers.results.MultipleDnsZoneDependenciesResult import MultipleDnsZoneDependenciesResult
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoRecordInCacheError import NoRecordInCacheError
from exceptions.NotWantedTLDError import NotWantedTLDError
from exceptions.ReachedMaximumRecursivePathThresholdError import ReachedMaximumRecursivePathThresholdError
from exceptions.UnknownReasonError import UnknownReasonError
from utils import list_utils


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

    def do_query(self, name: str, type_rr: TypesRR) -> Path:
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
        if type_rr == TypesRR.A:
            path_builder = APathBuilder()
        elif type_rr == TypesRR.NS:
            path_builder = NSPathBuilder()
        elif type_rr == TypesRR.CNAME:
            path_builder = CNAMEPathBuilder()
        elif type_rr == TypesRR.MX:
            path_builder = MXPathBuilder()
        else:
            raise ValueError
        try:
            answer = self.resolver.resolve(name, type_rr.to_string())
            canonical_name = None
            for cname in answer.chaining_result.cnames:
                for key in cname.items.keys():
                    current_rr = RRecord(DomainName(str(cname.name)), TypesRR.CNAME, [str(key.target)])
                    path_builder.add_alias(current_rr)
                    canonical_name = str(key.target)
            if canonical_name is None:
                canonical_name = name
            rr_values = list()
            for ad in answer:
                if isinstance(ad, Name):
                    rr_values.append(str(ad))
                else:
                    rr_values.append(ad.to_text())
            response_rr = RRecord(DomainName(canonical_name), type_rr, rr_values)
            path_builder.complete_resolution(response_rr)
            return path_builder.build()
        except dns.resolver.NXDOMAIN:  # name is a domain that does not exist
            raise DomainNonExistentError(name)
        except dns.resolver.NoAnswer:  # there is no answer
            raise NoAnswerError(name, type_rr)
        except (dns.resolver.NoNameservers, dns.resolver.YXDOMAIN) as e:
            raise UnknownReasonError(message=str(e))
        except Exception as e:  # fail because of another reason...
            raise UnknownReasonError(message=str(e))

    def resolve_access_path(self, web_site_domain_name: DomainName) -> APath:
        """
        This method resolves the domain name parameter (supposed to be extracted from an URL) in all the alias to
        follow before the IP address is resolved.

        :param web_site_domain_name: A domain name.
        :type web_site_domain_name: DomainName
        :raise NoAnswerError: If such error happen.
        :raise DomainNonExistentError: If such error happen.
        :raise UnknownReasonError: If such error happen.
        :return: A tuple containing first the A type RR answer, and then a list of CNAME type RR that represents the
        access path.
        :rtype: Tuple[RRecord, List[RRecord]]
        """
        try:
            a_path = self.cache.resolve_path(web_site_domain_name, TypesRR.A)
        except NoAvailablePathError:
            try:
                a_path = self.do_query(web_site_domain_name.string, TypesRR.A)
                self.cache.add_path(a_path, control_for_no_duplicates=True)
            except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
                raise
        return a_path

    def resolve_multiple_mail_domains(self, mail_domains: List[DomainName]) -> MultipleMailDomainResolvingResult:
        """
        This method resolves the mail servers dependencies of multiple mail domains.
        If something goes wrong, exceptions are not raised but the error_logs of the result will be populated with what
        went wrong.

        :param mail_domains: A list of mail domains.
        :param mail_domains: List[str]
        :return: A MultipleDnsMailServerDependenciesResult object.
        :rtype: MultipleMailDomainResolvingResult
        """
        final_results = MultipleMailDomainResolvingResult()
        for i, mail_domain in enumerate(mail_domains):
            print(f"Resolving mail domain[{i+1}/{len(mail_domains)}]: {mail_domain}")
            try:
                resolver_result = self.resolve_mail_domain(mail_domain)
                final_results.add_dependency(mail_domain, resolver_result)
                # prints
                print(f"{resolver_result.mail_domain_path.stamp()}")
                for j, mail_server in enumerate(resolver_result.mail_servers_paths.keys()):
                    if resolver_result.mail_servers_paths[mail_server] is not None:
                        print(f"--> mailserver[{j+1}/{len(resolver_result.mail_servers_paths.keys())}]: {resolver_result.mail_servers_paths[mail_server].stamp()}")
                    else:
                        print(
                            f"--> mailserver[{j + 1}/{len(resolver_result.mail_servers_paths.keys())}]: Unresolved A path")
            except (InvalidDomainNameError, NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
                print(f"!!! {str(e)} !!!")
                final_results.add_dependency(mail_domain, None)
                final_results.append_error_log(ErrorLog(e, mail_domain.string, str(e)))
            print()
        return final_results

    def resolve_mail_domain(self, mail_domain: DomainName) -> MailDomainResolvingResult:
        """
        This method resolves the mail servers dependencies of a mail domain.

        :param mail_domain: A mail domain.
        :type mail_domain: str
        :raise InvalidDomainNameError: If mail domain is not a well-formatted domain name or email address.
        :raise DomainNonExistentError: If query response says that name is a non-existent domain.
        :raise NoAnswerError: If query has no response.
        :raise UnknownReasonError: If query execution went wrong.
        :return: A DnsMailServersDependenciesResult object.
        :rtype: MailDomainResolvingResult
        """
        try:
            mx_path = self.do_query(mail_domain.string, TypesRR.MX)
        except (DomainNonExistentError, NoAnswerError, UnknownReasonError) as e:
            print(f"!!! {str(e)} !!!")
            raise
        result = MailDomainResolvingResult(mx_path)
        for value in mx_path.get_resolution().values:
            if isinstance(value, DomainName):
                mail_server = value
                try:
                    a_path = self.resolve_access_path(mail_server)
                except (NoAnswerError, UnknownReasonError, DomainNonExistentError) as e:
                    print(f"!!! {str(e)} ==> mail domain {mail_domain} is unresolved.!!!")
                    result.add_unresolved_mail_server_access(mail_server)
                    continue
                    # TODO: should propagate to log in the error_logger
                result.add_mail_server_access(a_path)
        return result

    def resolve_multiple_domains_dependencies(self, domain_list: List[DomainName], reset_cache_per_elaboration=False) -> MultipleDnsZoneDependenciesResult:
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
                final_results.error_logs.append(ErrorLog(e, domain.string, str(e)))
        return final_results

    def resolve_domain_dependencies(self, domain: DomainName) -> DnsZoneDependenciesResult:
        """
        This method resolves the zone dependencies of a domain name.

        :param domain: A domain name.
        :type domain: DomainName
        :raise InvalidDomainNameError: If domain name parameter is not a well-formatted domain name.
        :return: A DnsZoneDependenciesResult object.
        :rtype: DnsZoneDependenciesResult
        """
        error_logs = list()
        start_cache_length = len(self.cache.cache)
        elaboration_domains = domain.parse_subdomains(root_included=True, self_included=True)
        if len(elaboration_domains) == 0:
            raise InvalidDomainNameError(domain.string)  # TODO: giusto???
        zone_dependencies = set()  # si va a popolare con ogni iterazione
        cname_exception = False
        for_direct_zones = [domain]
        print(f"Cache has {start_cache_length} entries.")
        for current_domain in elaboration_domains:
            # is domain a nameserver with aliases?
            try:
                cname_path = self.resolve_cname(current_domain)
                for subdomain in cname_path.get_resolution().get_first_value().parse_subdomains(False, False):
                    list_utils.append_with_no_duplicates(elaboration_domains, subdomain)
                for rr in cname_path.get_aliases_chain():
                    for_direct_zones.append(rr.name)
                for_direct_zones.append(cname_path.get_resolution().name)
                for_direct_zones.append(cname_path.get_resolution().get_first_value())
            except NoAvailablePathError:
                cname_path = current_domain
            except (DomainNonExistentError, UnknownReasonError, ReachedMaximumRecursivePathThresholdError) as e:
                cname_exception = True
                cname_path = current_domain
            try:
                zone, names_to_be_elaborated, error_logs_to_be_added = self.resolve_zone(cname_path)
                for log in error_logs_to_be_added:
                    error_logs.append(log)
            except NotWantedTLDError:
                continue
            except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
                if cname_exception:
                    error_logs.append(ErrorLog(e, current_domain.string, str(e)))
                continue

            for name in names_to_be_elaborated:
                list_utils.append_with_no_duplicates(elaboration_domains, name)
            zone_dependencies.add(zone)

        zone_dependencies_per_nameserver, zone_dependencies_per_zone = self.extract_zone_dependencies(zone_dependencies)

        for name_server in zone_dependencies_per_nameserver.keys():
            for_direct_zones.append(name_server)
        direct_zones = self.extract_direct_zones(for_direct_zones, zone_dependencies)
        print(f"Dependencies recap: {len(zone_dependencies)} zones, {len(self.cache.cache) - start_cache_length} cache entries added, {len(error_logs)} errors.\n")
        return DnsZoneDependenciesResult(zone_dependencies, direct_zones, zone_dependencies_per_zone, zone_dependencies_per_nameserver, error_logs)

    def resolve_cname(self, name: DomainName) -> CNAMEPath:
        """
        This methods resolves the CNAME RR of the name parameter, then if there are more CNAME RR from the alias of the
        previous CNAME RR then recursively it will continue the resolving. It will stops when there are no other CNAME
        RR available for the last alias computed.
        In the end it will be created a sort of 'alias path'.

        :param name: A domain name.
        :type name: DomainName
        :param parameter_included: Decide if in the result list the parameter should be considered.
        :type parameter_included: bool
        :raise ReachedMaximumRecursivePathThresholdError: If the CNAME query consists in an endless cycle.
        :raise DomainNonExistentError: If during the CNAME query happens such error.
        :raise UnknownReasonError: If during the CNAME query happens such error.
        :raise NoAvailablePathError: If there's no path for name parameter.
        :return: The path of alias.
        :rtype: List[str]
        """
        try:
            cname_path_builder = self.__inner_resolve_cname(name, None, count_invocations_threshold=100)
        except ReachedMaximumRecursivePathThresholdError:
            raise ReachedMaximumRecursivePathThresholdError(name.string)
        except (DomainNonExistentError, UnknownReasonError, ReachedMaximumRecursivePathThresholdError):
            raise
        try:
            return cname_path_builder.complete().build()
        except IndexError:
            raise NoAvailablePathError(name.string)

    def __inner_resolve_cname(self, name: DomainName, path_builder: NSPathBuilder or None, count_invocations_threshold=1000, count_invocations=0) -> CNAMEPathBuilder:
        """
        Recursive auxiliary method used in the 'resolve_cname' method.

        :param name: A domain name.
        :type name: DomainName
        :param path: Result carried through all recursive invocations. None value corresponds to the initial seed.
        :type path: List[str] or None
        :param count_invocations: Number of recursive invocations of the method. 0 is the initial value obviously.
        :type count_invocations: int
        :param count_invocations_threshold: Threshold that sets the number beyond which it is considered that the
        resolution consists in a endless cycle.
        :type count_invocations_threshold: int
        :raise ReachedMaximumRecursivePathThresholdError: If the CNAME query consists in an endless cycle.
        :raise DomainNonExistentError: If during the CNAME query happens such error.
        :raise UnknownReasonError: If during the CNAME query happens a error that goes beyond the technical ones.
        :return: The path of alias.
        :rtype: List[str]
        """
        if path_builder is None:
            path_builder = CNAMEPathBuilder()
        else:
            pass
        count_invocations = count_invocations + 1
        if count_invocations >= count_invocations_threshold:
            raise ReachedMaximumRecursivePathThresholdError(name.string)
        # path.append(name)
        try:
            rr_answer = self.cache.lookup_first(name, TypesRR.CNAME)
        except NoRecordInCacheError:
            try:
                current_cname_path = self.do_query(name.string, TypesRR.CNAME)
                rr_answer = current_cname_path.get_resolution()
                self.cache.add_entry(rr_answer)
            except NoAnswerError:
                return path_builder
            except (DomainNonExistentError, UnknownReasonError):
                raise
        path_builder.add_alias(rr_answer)
        return self.__inner_resolve_cname(rr_answer.get_first_value(), path_builder, count_invocations_threshold=count_invocations_threshold, count_invocations=count_invocations)

    def resolve_zone(self, cname_param: CNAMEPath or DomainName) -> Tuple[Zone, List[DomainName], List[ErrorLog]]:
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
        error_logs_to_be_added = list()
        names_to_be_elaborated = set()
        if isinstance(cname_param, DomainName):
            last_domain_name = cname_param
            total_path_builder = NSPathBuilder()
        else:
            last_domain_name = cname_param.get_resolution().get_first_value()
            total_path_builder = NSPathBuilder.from_cname_path(cname_param)
        try:
            rr_answer = self.cache.lookup_first(last_domain_name, TypesRR.NS)
            total_path = total_path_builder.complete_resolution(rr_answer).build()
            if self.consider_tld == False and last_domain_name.is_tld():
                raise NotWantedTLDError
            print(f"Depends on zone: {rr_answer.name}\t\t\t[NON-AUTHORITATIVE]")
            for value in rr_answer.values:
                for domain in value.parse_subdomains(root_included=False, self_included=True):
                    names_to_be_elaborated.add(domain)
        except NoRecordInCacheError:
            try:
                current_path = self.do_query(last_domain_name.string, TypesRR.NS)
                self.cache.add_path(current_path)
                """
                if isinstance(cname_param, CNAMEPath):
                    total_path_builder = NSPathBuilder.from_cname_path(cname_param)
                else:
                    total_path_builder = NSPathBuilder()
                """
                for rr in current_path.get_aliases_chain():
                    names_to_be_elaborated.add(rr.get_first_value())
                    total_path_builder.add_alias(rr)
                total_path = total_path_builder.complete_resolution(current_path.get_resolution()).build()
                rr_answer = total_path.get_resolution()
                for value in rr_answer.values:
                    for domain in value.parse_subdomains(root_included=False, self_included=True):
                        names_to_be_elaborated.add(domain)
                if self.consider_tld == False and last_domain_name.is_tld():
                    raise NotWantedTLDError
                print(f"Depends on zone: {rr_answer.name}")
            except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
                raise

        name_servers_a_path = list()
        for name_server in total_path.get_resolution().values:
            try:
                a_path = self.cache.resolve_path(name_server, TypesRR.A)
            except NoAvailablePathError:
                # attempt for partially resolved path in cache
                try:
                    a_path, alias_subdomains = self.try_to_resolve_partially_cached_a_path(name_server)
                    for subdomain in alias_subdomains:
                        names_to_be_elaborated.add(subdomain)
                    name_servers_a_path.append(a_path)
                    continue
                except (DomainNonExistentError, UnknownReasonError) as e:
                    error_logs_to_be_added.append(ErrorLog(e, name_server.string, str(e)))
                except (NoAnswerError, NoAvailablePathError):
                    pass
                # normal elaboration
                try:
                    a_path = self.do_query(name_server.string, TypesRR.A)
                    self.cache.add_path(a_path)
                except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
                    error_logs_to_be_added.append(ErrorLog(e, name_server.string, str(e)))
                    continue
            name_servers_a_path.append(a_path)
        zone = Zone(total_path, name_servers_a_path)
        return zone, names_to_be_elaborated, error_logs_to_be_added

    def extract_zone_dependencies(self, zone_set: Set[Zone], with_self_zone=False) -> Tuple[Dict[DomainName, Set[Zone]], Dict[Zone, Set[Zone]]]:
        """
        This method extracts the zone dependencies for each name server and the zone dependencies for each zone name
        from the Zone (the application-defined object) list resolved.

        :param zone_set:
        :type zone_set: List[Zone]
        :return: A dictionary that associates all the name server to a list of zone names and then a dictionary that
        associates all zone names to a list of zone names, as a tuple.
        :rtype: Tuple[Dict[str, List[str]], Dict[str, List[str]]]
        """
        zone_dependencies_per_zone = dict()
        zone_dependencies_per_name_server = dict()
        for zone in zone_set:
            # resolve zone dependencies of zone
            try:
                zone_dependencies_per_zone[zone]
            except KeyError:
                zone_dependencies_per_zone[zone] = set()
            # zones = self.parse_zone_dependencies_of_zone(zone, zone_set, alias_encountered)
            zones = self.parse_zone_dependencies_of_zone(zone, zone_set)
            for zone_name in zones:
                zone_dependencies_per_zone[zone].add(zone_name)

            # resolve zone dependencies of name server
            for name_server_a_path in zone.name_servers:
                name_server = name_server_a_path.get_qname()
                try:
                    zone_dependencies_per_name_server[name_server]
                except KeyError:
                    zone_dependencies_per_name_server[name_server] = set()
                zones = self.parse_zone_dependencies_of_name_server(name_server, zone_set)
                for zone_name in zones:
                    zone_dependencies_per_name_server[name_server].add(zone_name)
        if not with_self_zone:
            # eliminate the self zone from its dependencies
            for zone in zone_set:
                try:
                    zone_dependencies_per_zone[zone].remove(zone)
                except KeyError:
                    pass
        return zone_dependencies_per_name_server, zone_dependencies_per_zone

    def parse_belonging_zones_of_name_server(self, name_server: DomainName, zones_set: Set[Zone]) -> Set[Zone]:
        # DA CANCELLARE
        result = set()
        for zone in zones_set:
            for name_server_of_zone in zone.nameservers():
                if name_server_of_zone == name_server:
                    result.add(zone)
        return result

    def parse_zone_dependencies_of_name_server(self, name_server: DomainName, zone_set: Set[Zone]) -> Set[Zone]:
        """
        This methods takes as data pool the Zone (the application-defined object) list resolved and extract the zone
        dependencies from the name_server parameter.

        :param name_server: A name server.
        :type name_server: str
        :param zone_set: All the Zone (the application-defined object) list resolved.
        :type zone_set: List[Zone]
        :return: A list of zone names.
        :rtype: List[str]
        """
        try:
            zone = self.extract_direct_zone(name_server, zone_set)
        except ValueError:
            # n.ns.at. case
            return set()
        return self.__inner_parse_zone_dependencies_of_zone(zone, zone_set)

    def parse_zone_dependencies_of_zone(self, current_zone: Zone, zone_set: Set[Zone]) -> Set[Zone]:
        """
        This methods takes as data pool the Zone (the application-defined object) list resolved and extract the zone
        dependencies from the current_zone parameter.

        :param current_zone: A Zone (the application-defined object) object.
        :type current_zone: Zone
        :param zone_set: All the Zone (the application-defined object) list resolved.
        :type zone_set: List[Zone]
        :return: A list of zone names.
        :rtype: List[str]
        """
        return self.__inner_parse_zone_dependencies_of_zone(current_zone, zone_set)

    def __inner_parse_zone_dependencies_of_zone(self, zones_param: Zone, zone_set: Set[Zone]) -> Set[Zone]:
        zones_to_be_elaborated = [zones_param]
        result = set()
        for zone in zones_to_be_elaborated:
            temp = self.__parse_zones_of_domain_names(zone.parse_every_domain_name(True, self.consider_tld, self.consider_tld), zone_set)
            result = result.union(temp)
            for z in result:
                list_utils.append_with_no_duplicates(zones_to_be_elaborated, z)
        return result

    def __parse_zones_of_domain_names(self, domain_names: Set[DomainName], zones_set: Set[Zone]) -> Set[Zone]:
        result = set()
        for domain_name in domain_names:
            for zone in zones_set:
                if domain_name == zone.name:
                    result.add(zone)
        return result


    def parse_zone_dependencies_of_zone_OLD(self, current_zone: Zone, zone_set: Set[Zone], alias_encountered: Dict[DomainName, CNAMEPath]) -> Set[Zone]:
        """
        This methods takes as data pool the Zone (the application-defined object) list resolved and extract the zone
        dependencies from the current_zone parameter.

        :param current_zone: A Zone (the application-defined object) object.
        :type current_zone: Zone
        :param zone_set: All the Zone (the application-defined object) list resolved.
        :type zone_set: List[Zone]
        :return: A list of zone names.
        :rtype: List[str]
        """
        zone_dependencies = set()
        # ancestor zones
        zones = self.__parse_zones_of_domain_name_from_zone_list(current_zone.name, zone_set)
        for zone in zones:
            zone_dependencies.add(zone)
        # zones from name servers
        for name_server in current_zone.nameservers(False):
            name_server_zones = self.__parse_zones_of_domain_name_from_zone_list(name_server, zone_set)
            for z in name_server_zones:
                zone_dependencies.add(z)
        return zone_dependencies

    def __parse_zones_of_domain_name_from_zone_list(self, name: DomainName, zone_set: Set[Zone]) -> List[Zone]:
        """
        This methods takes as data pool the Zone (the application-defined object) list resolved.
        Then it creates a list of domain names from the name parameter considering all the ancestor domain names and
        extract the zone dependencies from the data pool mentioned above.

        :param name: name
        :type name: str
        :param zone_set: The Zone (the application-defined object) list used as data pool.
        :type zone_set: List[Zone]
        :return: A list of Zone (the application-defined object).
        :rtype: List[Zone]
        """
        subdomains = name.parse_subdomains(root_included=True, self_included=False)
        result = list()
        for subdomain in subdomains:
            for zone in zone_set:
                if subdomain == zone.name:
                    result.append(zone)
        return result

    def try_to_resolve_partially_cached_a_path(self, name_server: DomainName) -> Tuple[APath, List[DomainName]]:
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
        #
        try:
            cname_path = self.do_query(name_server.string, TypesRR.CNAME)
        except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
            raise
        self.cache.add_path(cname_path)
        name_to_be_elaborated = list()
        for dn in name_server.parse_subdomains(True, True):
            name_to_be_elaborated.append(dn)
        #
        try:
            a_path = self.cache.resolve_path(cname_path.get_resolution().get_first_value(), TypesRR.A)
        except NoAvailablePathError:
            raise
        #
        total_path_builder = APathBuilder.from_cname_path(cname_path)
        for rr in a_path.get_aliases_chain():
            total_path_builder.add_alias(rr)
        total_path = total_path_builder.complete_resolution(a_path.get_resolution()).build()
        return total_path, name_to_be_elaborated

    def extract_direct_zones(self, domain_names: List[DomainName], zone_set: Set[Zone]) -> Dict[DomainName, Zone or None]:
        """
        This method extracts the direct zone of the domain name parameter from the zone_list parameter used as data
        pool.

        :param domain_name: A domain name.
        :type domain_name: str
        :param zone_set: All the Zone (the application-defined object) list resolved.
        :type zone_set: List[Zone]
        :raise ValueError: If there's no match from all the ancestor domain name as zone. Should never happen..
        :return: The direct zone name.
        :rtype: str
        """
        result = dict()
        for domain_name in domain_names:
            try:
                current_direct_zone = self.extract_direct_zone(domain_name, zone_set)
            except ValueError:
                current_direct_zone = None
            result[domain_name] = current_direct_zone
        return result

    def extract_direct_zone(self, domain_name: DomainName, zone_set: Set[Zone]) -> Zone:
        """
        This method extracts the direct zone of the domain name parameter from the zone_list parameter used as data
        pool.

        :param domain_name: A domain name.
        :type domain_name: str
        :param zone_set: All the Zone (the application-defined object) list resolved.
        :type zone_set: List[Zone]
        :raise ValueError: If there's no match from all the ancestor domain name as zone. Should never happen..
        :return: The direct zone name.
        :rtype: str
        """
        for_zone_name_subdomains = list(reversed(domain_name.parse_subdomains(root_included=True, self_included=False)))
        for current_domain in for_zone_name_subdomains:
            for zone in zone_set:
                if current_domain == zone.name:
                    if zone.name.is_tld() and not self.consider_tld:
                        raise ValueError
                    else:
                        return zone
        raise ValueError
