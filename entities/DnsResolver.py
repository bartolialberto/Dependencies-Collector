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

    def do_query(self, name: str, type_rr: TypesRR) -> Tuple[RRecord, RRecord]:
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
            for cname in answer.chaining_result.cnames:
                for key in cname.items.keys():
                    rr_aliases.append(str(key.target))
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
            cname_rrecords = RRecord(name, TypesRR.CNAME, rr_aliases)
            rr_values = list()
            for ad in answer:
                if isinstance(ad, Name):
                    rr_values.append(str(ad))
                else:
                    rr_values.append(ad.to_text())
            response_rrecords = RRecord(answer.canonical_name.to_text(), type_rr, rr_values)
            return response_rrecords, cname_rrecords
        except dns.resolver.NXDOMAIN:  # name is a domain that does not exist
            raise DomainNonExistentError(name)
        except dns.resolver.NoAnswer:  # there is no answer
            raise NoAnswerError(name, type_rr)
        except (dns.resolver.NoNameservers, dns.resolver.YXDOMAIN) as e:
            raise UnknownReasonError(message=str(e))
        except Exception as e:  # fail because of another reason...
            raise UnknownReasonError(message=str(e))

    def resolve_multiple_domains_dependencies(self, domain_list: List[str]) -> Tuple[Dict[str, List[Zone]], Dict[str, List[Zone]], Dict[str, List[str]], List[ErrorLog]]:
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
                dns_result, temp_zone_links, temp_nameservers, temp_logs = self.resolve_domain_dependencies(domain, zone_dependencies=zone_links)

                # insert domain dns dependencies
                results[domain] = dns_result

                # merge zone dependencies
                zone_links.update(temp_zone_links)

                # merge nameservers
                """
                for ns in temp_nameservers:
                    try:
                        nameservers[ns]
                        for zone_name in temp_nameservers[ns]:
                            list_utils.append_with_no_duplicates(nameservers[ns], zone_name)
                    except KeyError:
                        nameservers[ns] = list()
                        for zone_name in temp_nameservers[ns]:
                            nameservers[ns].append(zone_name)
                """
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

    def resolve_domain_dependencies(self, domain: str, zone_dependencies=None):
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
        if zone_dependencies is None:
            zone_dependencies = dict()
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
            if current_domain == 'nse12.o365filtering.com':
                print('')
                pass

            # reset all variables for new iteration
            current_zone_nameservers = list()
            current_zone_cnames = list()
            current_zone_name = '_'
            rr_zone_values = None
            rr_zone_aliases = None
            rr_ns = None
            zone_name_of_nameserver = None

            # is domain a nameserver with aliases?
            try:
                # aliases = self.cache.look_up_first_alias(current_domain)
                aliases = self.cache.look_up_all_aliases(current_domain)
                for alias in aliases:
                    try:
                        zones = self.cache.resolve_zones_from_alias(alias)
                        if len(zones) != 0:
                            # continue
                            break
                        for z in zones:
                            current_zone_name = z[0]
                            current_zone_nameservers = z[1]
                            current_zone_cnames = z[2]
                            zone = Zone(current_zone_name, current_zone_nameservers, current_zone_cnames)
                            for nm in current_zone_nameservers:
                                self._split_domain_name_and_add_to_list(subdomains, nm.name, False)
                            if zone not in zone_list:
                                print(f"Depends on zone: {current_zone_name}\t\t\t[NON-AUTHORITATIVE]")
                                zone_list.append(zone)
                                # list_utils.append_with_no_duplicates(zone_list, Zone(current_zone_name, current_zone_nameservers, current_zone_cnames))
                        # continue
                        break
                    except NoRecordInCacheError:
                        pass
            except NoRecordInCacheError:
                try:
                    rr_zone_values, rr_zone_aliases = self.do_query(current_domain, TypesRR.CNAME)
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
                current_zone_name, current_zone_nameservers, current_zone_cnames = self.cache.resolve_zone_from_ns_rr(rr_ns)  # raise NoRecordInCacheError too

                """
                #
                try:
                    zone_dependencies[current_domain]
                except KeyError:
                    zone_dependencies[current_domain] = list()
                finally:
                    try:
                        zone_links[current_domain]
                    except KeyError:
                        zone_links[current_domain] = list()
                """
                try:
                    zone_links[current_domain]
                except KeyError:
                    zone_links[current_domain] = set()

                for rr in current_zone_nameservers:
                    self._split_domain_name_and_add_to_list(subdomains, rr.name, False)

                    #
                    """
                    self._split_domain_name_and_add_to_list(zone_links[current_domain], rr.name, False)
                    try:
                        nameservers[rr.name]
                    except KeyError:
                        nameservers[rr.name] = list()
                    finally:
                        list_utils.append_with_no_duplicates(nameservers[rr.name], current_zone_name)
                    """
                    try:
                        zone_name_of_nameserver = self.resolve_zone_of_nameserver(rr.name)
                        zone_links[current_domain].add(zone_name_of_nameserver)
                    except ValueError:
                        pass
                    try:
                        nameservers[rr.name]
                    except KeyError:
                        nameservers[rr.name] = set()
                    finally:
                        nameservers[rr.name].add(current_zone_name)

                zone = Zone(current_zone_name, current_zone_nameservers, current_zone_cnames)
                if zone not in zone_list:
                    print(f"Depends on zone: {current_zone_name}\t\t\t[NON-AUTHORITATIVE]")
                    zone_list.append(zone)
            except NoRecordInCacheError:
                try:
                    rr_zone_values, rr_zone_aliases = self.do_query(current_domain, TypesRR.NS)
                except NoAnswerError:
                    # log error???
                    # current_name non è niente???
                    continue
                except (DomainNonExistentError, UnknownReasonError) as e:
                    error_logs.append(ErrorLog(e, current_domain, str(e)))
                    continue
                current_zone_name = rr_zone_values.name
                self.cache.add_entry(rr_zone_values)

                #
                """
                try:
                    zone_dependencies[current_domain]
                except KeyError:
                    zone_dependencies[current_domain] = list()
                finally:
                    try:
                        zone_links[current_domain]
                    except KeyError:
                        zone_links[current_domain] = list()
                """
                try:
                    zone_links[current_domain]
                except KeyError:
                    zone_links[current_domain] = set()

                # no rr_aliases poiché una query NS non può avere alias
                for nameserver in rr_zone_values.values:
                    # per ogni nameserver devo considerare che potrebbero esserci già dei RR di tipo A ed il nameserver
                    # corrente è solo un alias di uno di quei nameserver che ha già (appunto) rr di tipo A nella cache,
                    # quindi in verità è già risolto (==> non server metterlo in cache, sennò ho doppioni)
                    try:
                        rr_a_cache = self.cache.resolve_path_from_alias(nameserver)
                        list_utils.append_with_no_duplicates(current_zone_nameservers, rr_a_cache)  # ma se il RR ha solo il campo values diverso?
                    except NoRecordInCacheError:
                        try:
                            rr_nameserver_values, rr_nameserver_aliases = self.do_query(nameserver, TypesRR.A)
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
                    self._split_domain_name_and_add_to_list(subdomains, nameserver, False)

                    #
                    """
                    self._split_domain_name_and_add_to_list(zone_links[current_domain], nameserver, False)
                    try:
                        nameservers[nameserver]
                    except KeyError:
                        nameservers[nameserver] = list()
                    finally:
                        list_utils.append_with_no_duplicates(nameservers[nameserver], current_zone_name)
                    """
                    try:
                        zone_name_of_nameserver = self.resolve_zone_of_nameserver(nameserver)
                        zone_links[current_domain].add(zone_name_of_nameserver)
                    except ValueError:
                        pass
                    try:
                        nameservers[nameserver]
                    except KeyError:
                        nameservers[nameserver] = set()
                    finally:
                        nameservers[nameserver].add(current_zone_name)

                print(f"Depends on zone: {current_zone_name}")
                zone_list.append(Zone(current_zone_name, current_zone_nameservers, current_zone_cnames))
        print(f"Dependencies recap: {len(zone_list)} zones, {len(self.cache.cache) - start_cache_length} cache entries added, {len(error_logs)} errors.\n")

        """
        # eliminare chiavi che hanno liste vuote
        for zone_name in zone_links.keys():
            if len(zone_dependencies[zone_name]) != 0:
                try:
                    zone_dependencies[zone_name].remove(zone_name)
                except ValueError:
                    pass
                continue
            to_be_removed = set()
            for relationship in zone_links[zone_name]:
                if not domain_name_utils.equals(relationship, zone_name):
                    try:
                        self.cache.look_up_first(relationship, TypesRR.NS)
                    except NoRecordInCacheError:
                        to_be_removed.add(relationship)     # cannot remove directly 'cause we are still iterating
            for relationship in to_be_removed:
                zone_links[zone_name].remove(relationship)
            for zone_dependency in zone_links[zone_name]:
                tmp = self.cache.resolve_zone_from_zone_name(zone_dependency)
                zone_dependencies[zone_name].append(Zone(tmp[0], tmp[1], tmp[2]))
        """
            # TODO: togliere i Top-Level Domain

        return zone_list, zone_links, nameservers, error_logs

    def resolve_zone_of_nameserver(self, nameserver: str):
        subdomains = domain_name_utils.get_subdomains_name_list(nameserver, False)
        for domain in reversed(subdomains):
            try:
                rr = self.cache.look_up_first(domain, TypesRR.NS)
                return domain
            except NoRecordInCacheError:
                try:
                    rr_values, rr_aliases = self.do_query(domain, TypesRR.NS)
                    self.cache.add_entry(rr_values)
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
