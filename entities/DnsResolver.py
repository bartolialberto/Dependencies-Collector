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
    def __init__(self, tld_list: List[str] or None):
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

    def resolve_multiple_domains_dependencies(self, domain_list: List[str], reset_cache_per_elaboration=False, consider_tld=True) -> Tuple[Dict[str, List[Zone]], Dict[str, List[str]], Dict[str, List[str]], List[ErrorLog]]:
        """
        This method resolves the zone dependencies of a list of domain names.

        :param domain_list: A list of domain names.
        :type domain_list: List[str]
        :raise :
        :return: A tuple containing a dictionary in which each key is a domain name of the domain names list parameter,
        and the value is the list of zone; as second element of the tuple there's the list of error logs.
        :rtype: Tuple[Dict[str: List[Zone]], List[ErrorLog]]
        """
        dns_results = dict()
        error_logs = list()
        zone_dependencies_per_zone = dict()
        zone_dependencies_per_nameserver = dict()
        for domain in domain_list:
            try:
                if reset_cache_per_elaboration:
                    self.cache.clear()

                temp_dns_result, temp_zone_dep_per_zone, temp_zone_dep_per_nameserver, temp_error_logs = self.resolve_domain_dependencies(domain, consider_tld=consider_tld)

                # insert domain dns dependencies
                dns_results[domain] = temp_dns_result

                # merge zone dependencies
                zone_dependencies_per_zone.update(temp_zone_dep_per_zone)

                # merge nameservers
                # zone_dependencies_per_nameserver.update(temp_zone_dep_per_nameserver)
                self.merge_zone_dependencies_per_nameserver_result(zone_dependencies_per_nameserver, temp_zone_dep_per_nameserver)

                # merge error logs
                for log in temp_error_logs:
                    error_logs.append(log)

            except InvalidDomainNameError as e:
                error_logs.append(ErrorLog(e, domain, str(e)))

        return dns_results, zone_dependencies_per_zone, zone_dependencies_per_nameserver, error_logs

    def resolve_multiple_mail_domains(self, mail_domains: List[str]) -> Tuple[Dict[str, List[str]], List[ErrorLog]]:
        results = dict()
        error_logs = list()
        for mail_domain in mail_domains:
            try:
                results[mail_domain] = self.resolve_mail_domain(mail_domain)
            except (InvalidDomainNameError, NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
                error_logs.append(ErrorLog(e, mail_domain, str(e)))
        return results, error_logs

    def resolve_mail_domain(self, mail_domain: str) -> List[str]:
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
        except (DomainNonExistentError, UnknownReasonError):
            raise
        for value in mx_values.values:
            result.append(value)
        return result

    def resolve_domain_dependencies(self, domain: str, consider_tld=True):
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
                            self._split_domain_name_and_add_to_list(elaboration_domains, nm.name, False)
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
                        # rr_a_cache = self.cache.resolve_path_also_from_alias(nameserver)
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

        if not consider_tld:
            zone_list, zone_dependencies_per_zone, zone_dependencies_per_nameserver = self._remove_tld(self.tld_list, zone_list, zone_dependencies_per_zone, zone_dependencies_per_nameserver)
        return zone_list, zone_dependencies_per_zone, zone_dependencies_per_nameserver, error_logs

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

    @classmethod
    def _remove_tld(cls, tld_list: List[str], zone_list: List[Zone], zone_dependencies_per_zone: Dict[str, List[str]], zone_dependencies_per_nameserver: Dict[str, List[str]]) -> Tuple[List[Zone], Dict[str, List[str]], Dict[str, List[str]]]:
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

    @classmethod
    def merge_zone_dependencies_per_nameserver_result(cls, total_result: Dict[str, List[str]], current_result: Dict[str, List[str]]):
        for nameserver in current_result.keys():
            try:
                total_result[nameserver]
            except KeyError:
                total_result[nameserver] = list()
            finally:
                for zone_dep in current_result[nameserver]:
                    list_utils.append_with_no_duplicates(total_result[nameserver], zone_dep)
