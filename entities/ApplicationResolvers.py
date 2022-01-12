import ipaddress
from typing import List, Dict, Tuple, Set
import selenium
from entities.ScriptDependenciesResolver import ScriptDependenciesResolver, MainPageScript
from entities.DnsResolver import DnsResolver
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.IpAsDatabase import IpAsDatabase, EntryIpAsDatabase
from entities.LandingResolver import LandingResolver, SiteLandingResult
from entities.ROVPageScraper import ROVPageScraper
from entities.TLDPageScraper import TLDPageScraper
from entities.Zone import Zone
from entities.error_log.ErrorLog import ErrorLog
from entities.error_log.ErrorLogger import ErrorLogger
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError
from utils import file_utils, requests_utils, list_utils, domain_name_utils, url_utils


class ApplicationResolvers:
    """
    This class represents the resolvers of the application all in one. Thanks to this it can track and handle all the
    results of each component and save all of them as object state (instance attributes).

    ...

    Attributes
    ----------
    _dns_resolver : DnsResolver
        Instance of a DnsResolver object.
    _ip_as_database : IpAsDatabase
        Instance of a IpAsDatabase object.
    _headless_browser : FirefoxHeadlessWebDriver
        Instance of a FirefoxHeadlessWebDriver object.
    _content_resolver : ContentDependenciesResolver
        Instance of a ContentDependenciesResolver object.
    _rov_page_scraper : ROVPageScraper
        Instance of a ROVPageScraper object.
    _error_logger : ErrorLogger
        Instance of a ApplicationErrorLogger object.
    _total_domain_names : List[str]
        List of all domain names.
    _total_dns_results : Dict[str: List[Zone]]
        Dictionary of all results of each execution of _dns_resolver.
    _total_ip_as_db_results : Dict[str: Tuple[str, EntryIpAsDatabase or None, ipaddress.IPv4Network or None]]
        Dictionary of all results of each execution of _ip_as_database.
    _total_landing_page_results : Dict[str: Tuple[str, List[str], bool]
        Dictionary of all results of each invocation of the resolve_landing_page method in requests_utils.
    _total_content_dependencies_results : Dict[str: List[ContentDependencyEntry]]
        Dictionary of all results of each execution of _content_resolver.
    _total_rov_page_scraper_results : Dict[int: Dict[str: List[str or EntryIpAsDatabase or IPv4Network or RowPrefixesTable or None]]]
        Dictionary of all results of each execution of _rov_page_scraper.
    """
    def __init__(self, consider_tld=False):
        """
        Initialize all components from scratch.
        Here is checked the presence of the geckodriver executable and the presence of the .tsv database.
        If the latter is absent then automatically it will be downloaded and put in the input folder.

        """
        self.landing_resolver = LandingResolver()
        try:
            self.headless_browser = FirefoxHeadlessWebDriver()
        except (FileWithExtensionNotFoundError, selenium.common.exceptions.WebDriverException) as e:
            print(f"!!! {str(e)} !!!")
            return
        if not consider_tld:
            self._tld_scraper = TLDPageScraper(self.headless_browser)
            try:
                tlds = self._tld_scraper.scrape_tld()
            except (selenium.common.exceptions.WebDriverException, selenium.common.exceptions.NoSuchElementException) as e:
                print(f"!!! {str(e)} !!!")
                return
        else:
            tlds = None
        self.dns_resolver = DnsResolver(tlds)
        try:
            self.dns_resolver.cache.load_csv_from_output_folder()
        except (ValueError, FilenameNotFoundError, OSError) as exc:
            print(f"!!! {str(exc)} !!!")
        tsv_db_is_updated = file_utils.is_tsv_database_updated()
        if tsv_db_is_updated:
            print("> .tsv database file is updated.")
        else:
            print("> Latest .tsv database (~25 MB) is downloading and extracting... ", end='')
            requests_utils.download_latest_tsv_database()
            print("DONE.")
        try:
            self.ip_as_database = IpAsDatabase()
        except (FileWithExtensionNotFoundError, OSError) as e:
            print(f"!!! {str(e)} !!!")
            exit(1)
        self.script_resolver = ScriptDependenciesResolver(self.headless_browser)
        self.rov_page_scraper = ROVPageScraper(self.headless_browser)
        self.error_logger = ErrorLogger()
        self.landing_web_sites_results = dict()
        self.landing_script_sites_results = dict()
        self.web_site_script_dependencies = dict()
        self.script_script_site_dependencies = tuple()
        self.mail_servers_results = dict()
        self.total_dns_results = dict()
        self.total_zone_dependencies_per_zone = dict()
        self.total_zone_dependencies_per_name_server = dict()
        self.total_ip_as_db_results = dict()
        self.total_landing_page_results = dict()
        self.total_content_dependencies_results = dict()
        self.total_rov_page_scraper_results = dict()

    def do_preamble_execution(self, web_sites: List[str], mail_domains: List[str]) -> List[str]:
        # elaboration
        self.landing_web_sites_results = self.do_web_site_landing_resolving(set(web_sites))
        self.mail_servers_results, temp_error_logs = self.dns_resolver.resolve_multiple_mail_domains(mail_domains)
        self.error_logger.add_entries(temp_error_logs)
        return self._extract_domain_names_from_preamble(mail_domains)

    def do_midst_execution(self, domain_names: List[str]) -> List[str]:
        # elaboration
        current_dns_results, current_zone_dep_per_zone, current_zone_dep_per_name_server = self.do_dns_resolving(domain_names)
        current_ip_as_db_results = self.do_ip_as_database_resolving(current_dns_results)
        self.web_site_script_dependencies = self.do_script_dependencies_resolving()

        # extracting
        self.script_script_site_dependencies, script_sites = self._extract_script_hosting_dependencies()
        self.landing_script_sites_results = self.do_script_site_landing_resolving(script_sites)

        # merging results
        ApplicationResolvers.merge_current_dict_to_total(self.total_dns_results, current_dns_results)
        ApplicationResolvers.merge_current_dict_to_total(self.total_zone_dependencies_per_zone, current_zone_dep_per_zone)
        ApplicationResolvers.merge_current_dict_to_total(self.total_zone_dependencies_per_name_server, current_zone_dep_per_name_server)
        ApplicationResolvers.merge_current_dict_to_total(self.total_ip_as_db_results, current_ip_as_db_results)

        return self._extract_domain_names_from_landing_script_sites_results()

    def do_epilogue_execution(self, domain_names: List[str]) -> None:
        # elaboration
        current_dns_results, current_zone_dep_per_zone, current_zone_dep_per_name_server = self.do_dns_resolving(domain_names)
        current_ip_as_db_results = self.do_ip_as_database_resolving(current_dns_results)

        # merging results
        ApplicationResolvers.merge_current_dict_to_total(self.total_dns_results, current_dns_results)
        ApplicationResolvers.merge_current_dict_to_total(self.total_zone_dependencies_per_zone, current_zone_dep_per_zone)
        ApplicationResolvers.merge_current_dict_to_total(self.total_zone_dependencies_per_name_server, current_zone_dep_per_name_server)
        ApplicationResolvers.merge_current_dict_to_total(self.total_ip_as_db_results, current_ip_as_db_results)

        # elaboration
        reformat_dict = ApplicationResolvers._reformat_entries(self.total_ip_as_db_results)
        self.total_rov_page_scraper_results = self.do_rov_page_scraping(reformat_dict)

    def do_web_site_landing_resolving(self, web_sites: Set[str]) -> Dict[str, Tuple[SiteLandingResult, SiteLandingResult]]:
        print("\n\nSTART WEB SITE LANDING RESOLVER")
        results, error_logs = self.landing_resolver.resolve_web_sites(web_sites)
        self.error_logger.add_entries(error_logs)
        print("END WEB SITE LANDING RESOLVER")
        return results

    def do_script_site_landing_resolving(self, script_sites: Set[str]) -> Dict[str, Tuple[SiteLandingResult, SiteLandingResult]]:
        print("\n\nSTART SCRIPT SITE LANDING RESOLVER")
        results, error_logs = self.landing_resolver.resolve_script_sites(script_sites)
        self.error_logger.add_entries(error_logs)
        print("END SCRIPT SITE LANDING RESOLVER")
        return results

    def do_dns_resolving(self, domain_names: List[str]) -> Tuple[Dict[str, List[Zone]], Dict[str, List[str]], Dict[str, List[str]]]:
        """
        DNS resolver elaboration. Given a list of domain names, it search and resolve the zone dependencies of each
        domain name. The result is a dictionary in which the key is the domain name, and the value is the list of Zones.

        :param domain_names: A list of domain names.
        :type domain_names: List[str]
        :return: A dictionary in which the key is a domain name and the value is the list of Zones on which the domain
        name depends.
        :rtype: Dict[str: List[Zone]]
        """
        print("\n\nSTART DNS DEPENDENCIES RESOLVER")
        self.dns_resolver.cache.take_snapshot()
        dns_results, zone_dependencies_per_zone, zone_dependencies_per_nameserver, error_logs = self.dns_resolver.resolve_multiple_domains_dependencies(domain_names)
        print("END DNS DEPENDENCIES RESOLVER")
        return dns_results, zone_dependencies_per_zone, zone_dependencies_per_nameserver

    def do_ip_as_database_resolving(self, dns_results: dict) -> Dict[str, Tuple[ipaddress.IPv4Address, EntryIpAsDatabase or None, ipaddress.IPv4Network or None]]:
        """
        .tsv database elaboration. Given the result of the DNS resolver, this component tries to match every IP address
        associated with every nameserver in the DNS result to a row of the .tsv database (in particular tries to find a
        IP range in which the IP address is contained). If an entry is found, then the belonging network from the
        summarized network range (see https://docs.python.org/3/library/ipaddress.html#ipaddress.summarize_address_range)
        is computed.
        If the entry or the belonging network has no match, then None is set in the result.

        :param dns_results: Dictionary from the DNS elaboration.
        :type dns_results: Dict[str: List[Zone]]
        :return: The results as a dictionary in which the key is a nameserver, and the value is a 3 elements long tuple
        containing: the IP address as string, the entry and the belonging network.
        :rtype: Dict[str: Tuple[str, EntryIpAsDatabase or None, ipaddress.IPv4Network or None]]
        """
        print("\n\nSTART IP-AS RESOLVER")
        ip_as_db_entries_result = dict()
        zone_obj_dict = dict()
        for domain_name in dns_results.keys():
            for zone in dns_results[domain_name]:
                try:
                    zone_obj_dict[zone.name]
                except KeyError:
                    zone_obj_dict[zone.name] = zone
        for index_domain, domain in enumerate(dns_results.keys()):
            print(f"Handling domain[{index_domain}] '{domain}'")
            for index_zone, zone in enumerate(dns_results[domain]):
                print(f"--> Handling zone[{index_zone}] '{zone.name}'")
                for i, nameserver in enumerate(zone.nameservers):
                    try:
                        # TODO: gestire più indirizzi per nameserver
                        try:
                            rr = zone.resolve_nameserver(nameserver)
                        except NoAvailablePathError:
                            # cosa fare???
                            pass
                        ip = ipaddress.IPv4Address(rr.get_first_value())
                        entry = self.ip_as_database.resolve_range(ip)
                        try:
                            belonging_network_ip_as_db, networks = entry.get_network_of_ip(ip)
                            print(
                                f"----> for nameserver[{i}] '{nameserver}' ({ip.compressed}) found AS{str(entry.as_number)}: [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. Belonging network: {belonging_network_ip_as_db.compressed}")
                            ip_as_db_entries_result[rr.name] = (ip, entry, belonging_network_ip_as_db)
                        except ValueError as exc:
                            print(
                                f"----> for nameserver[{i}] '{nameserver}' ({ip.compressed}) found AS record: [{entry}]")
                            self.error_logger.add_entry(ErrorLog(exc, ip.compressed,
                                                                 f"Impossible to compute belonging network from AS{str(entry.as_number)} IP range [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]"))
                            ip_as_db_entries_result[rr.name] = (ip, entry, None)
                    except AutonomousSystemNotFoundError as exc:
                        print(f"----> for nameserver[{i}] '{nameserver}' ({ip.compressed}) no AS found.")
                        self.error_logger.add_entry(
                            ErrorLog(exc, ip.compressed, f"No AS found in the database."))
                        ip_as_db_entries_result[rr.name] = (ip, None, None)
        print("END IP-AS RESOLVER")
        return ip_as_db_entries_result

    def do_script_dependencies_resolving(self) -> Dict[str, Tuple[Set[MainPageScript] or None, Set[MainPageScript] or None]]:
        print("\n\nSTART SCRIPT DEPENDENCIES RESOLVER")
        script_dependencies_result = dict()
        for website in self.landing_web_sites_results.keys():
            print(f"Searching script dependencies for website: {website}")
            https_result = self.landing_web_sites_results[website][0]
            http_result = self.landing_web_sites_results[website][1]

            if https_result is None and http_result is None:
                print(f"!!! Neither HTTPS nor HTTP landing possible for: {website} !!!")
            elif https_result is None and http_result is not None:
                # HTTPS
                print(f"******* via HTTPS *******")
                print(f"--> No landing possible")
                # HTTP
                print(f"******* via HTTP *******")
                http_landing_page = http_result.url
                try:
                    http_scripts = self.script_resolver.search_script_application_dependencies(http_landing_page)
                    for i, script in enumerate(http_scripts):
                        print(f"script[{i+1}/{len(http_scripts)}]: integrity={script.integrity}, src={script.src}")
                    script_dependencies_result[website] = (None, http_scripts)
                except selenium.common.exceptions.WebDriverException as e:
                    print(f"!!! {str(e)} !!!")
                    http_scripts = None
                    self.error_logger.add_entry(ErrorLog(e, http_landing_page, str(e)))
            elif http_result is None and https_result is not None:
                # HTTP
                print(f"******* via HTTP *******")
                print(f"--> No landing possible")
                # HTTPS
                print(f"******* via HTTPS *******")
                https_landing_page = https_result.url
                try:
                    https_scripts = self.script_resolver.search_script_application_dependencies(https_landing_page)
                    for i, script in enumerate(https_scripts):
                        print(f"script[{i+1}/{len(https_scripts)}]: integrity={script.integrity}, src={script.src}")
                    script_dependencies_result[website] = (https_scripts, None)
                except selenium.common.exceptions.WebDriverException as e:
                    print(f"!!! {str(e)} !!!")
                    https_scripts = None
                    self.error_logger.add_entry(ErrorLog(e, https_landing_page, str(e)))
                except Exception:
                    print('')
            else:
                # HTTPS
                print(f"******* via HTTPS *******")
                https_landing_page = https_result.url
                try:
                    https_scripts = self.script_resolver.search_script_application_dependencies(https_landing_page)
                    for i, script in enumerate(https_scripts):
                        print(f"script[{i+1}/{len(https_scripts)}]: integrity={script.integrity}, src={script.src}")
                except selenium.common.exceptions.WebDriverException as e:
                    print(f"!!! {str(e)} !!!")
                    https_scripts = None
                    self.error_logger.add_entry(ErrorLog(e, https_landing_page, str(e)))

                # HTTP
                print(f"******* via HTTP *******")
                http_landing_page = http_result.url
                try:
                    http_scripts = self.script_resolver.search_script_application_dependencies(http_landing_page)
                    for i, script in enumerate(https_scripts):
                        print(f"script[{i+1}/{len(https_scripts)}]: integrity={script.integrity}, src={script.src}")
                except selenium.common.exceptions.WebDriverException as e:
                    print(f"!!! {str(e)} !!!")
                    http_scripts = None
                    self.error_logger.add_entry(ErrorLog(e, http_landing_page, str(e)))
                script_dependencies_result[website] = (https_scripts, http_scripts)
            print('')
        print("END SCRIPT DEPENDENCIES RESOLVER")
        return script_dependencies_result

    def do_rov_page_scraping(self, reformat_dict: Dict[int, Dict[str, List[str or EntryIpAsDatabase or ipaddress.IPv4Network]] or None]) -> Dict[int, Dict[str, List[str or EntryIpAsDatabase or ipaddress.IPv4Network]] or None]:
        """
        ROV Page scraping. This method takes all the results of the .tsv database elaboration (saved in the state of
        self object) and scrapes all the AS pages in search of a valid entry in the prefixes table.

        :returns: The results as a dictionary in which the key is an AS number, and the value is a list of 4 elements
        (not a tuple because the elements are mutable). The elements are: the ip as string, the entry of the .tsv
        database, the belonging network computation from the .tsv database or None, the ROVPage entry or None.
        :rtype: Dict[int: Dict[str: List[str or EntryIpAsDatabase or IPv4Network or RowPrefixesTable or None]]]
        """
        print("\n\nSTART ROV PAGE SCRAPING")
        # reformat_dict = ApplicationResolvers._reformat_entries(self._total_ip_as_db_results)
        for as_number in reformat_dict.keys():
            print(f"Loading page for AS{as_number}")
            try:
                self.rov_page_scraper.load_as_page(as_number)
            except selenium.common.exceptions.WebDriverException as exc:
                print(f"!!! {str(exc)} !!!")
                # non tengo neanche traccia di ciò
                reformat_dict[as_number] = None
                self.error_logger.add_entry(ErrorLog(exc, "AS"+str(as_number), str(exc)))
                continue
            except (TableNotPresentError, ValueError, TableEmptyError, NotROVStateTypeError) as exc:
                print(f"!!! {str(exc)} !!!")
                reformat_dict[as_number] = None
                # entries_result_by_as.pop(as_number)       # tenerlo oppure no?
                self.error_logger.add_entry(ErrorLog(exc, "AS"+str(as_number), str(exc)))
                continue
            for nameserver in reformat_dict[as_number].keys():
                ip_string = reformat_dict[as_number][nameserver][0]
                entry_ip_as_db = reformat_dict[as_number][nameserver][1]
                belonging_network_ip_as_db = reformat_dict[as_number][nameserver][2]
                try:
                    row = self.rov_page_scraper.get_network_if_present(ipaddress.ip_address(ip_string))  # non gestisco ValueError perché non può accadere qua
                    reformat_dict[as_number][nameserver].append(row)
                    print(f"--> for '{nameserver}' ({ip_string}), found row: {str(row)}")
                except TableNotPresentError as exc:
                    print(f"!!! {exc.message} !!!")
                    reformat_dict[as_number][nameserver].append(None)
                    self.error_logger.add_entry(ErrorLog(exc, ip_string, str(exc)))
                except TableEmptyError as exc:
                    print(f"!!! {exc.message} !!!")
                    reformat_dict[as_number][nameserver].append(None)
                    self.error_logger.add_entry(ErrorLog(exc, ip_string, str(exc)))
                except NetworkNotFoundError as exc:
                    print(f"!!! {exc.message} !!!")
                    reformat_dict[as_number][nameserver].append(None)
                    self.error_logger.add_entry(ErrorLog(exc, ip_string, str(exc)))
        print("END ROV PAGE SCRAPING")
        # self.total_rov_page_scraper_results = reformat_dict
        return reformat_dict

    def _extract_domain_names_from_preamble(self, mail_domains: List[str]) -> List[str]:
        domain_names = list()
        # adding domain names from webservers
        for website in self.landing_web_sites_results.keys():
            https_webserver = self.landing_web_sites_results[website][0].server
            http_webserver = self.landing_web_sites_results[website][1].server
            list_utils.append_with_no_duplicates(domain_names, domain_name_utils.deduct_domain_name(https_webserver))
            list_utils.append_with_no_duplicates(domain_names, domain_name_utils.deduct_domain_name(http_webserver))
        # adding domain names from mail_domains and mailservers
        for mail_domain in mail_domains:
            list_utils.append_with_no_duplicates(domain_names, mail_domain)
            for mailserver in self.mail_servers_results:
                list_utils.append_with_no_duplicates(domain_names, mailserver)
        return domain_names

    def _extract_domain_names_from_landing_script_sites_results(self) -> List[str]:
        domain_names = list()
        for script_site in self.landing_script_sites_results.keys():
            https_result = self.landing_script_sites_results[script_site][0]
            if https_result is not None:
                list_utils.append_with_no_duplicates(domain_names, domain_name_utils.deduct_domain_name(https_result.server))
            http_result = self.landing_script_sites_results[script_site][1]
            if http_result is not None:
                list_utils.append_with_no_duplicates(domain_names, domain_name_utils.deduct_domain_name(http_result.server))
        return domain_names

    def _extract_script_hosting_dependencies(self) -> Tuple[Dict[MainPageScript, Set[str]], Set[str]]:
        result = dict()
        script_sites = set()
        for web_site in self.web_site_script_dependencies.keys():
            https_scripts = self.web_site_script_dependencies[web_site][0]
            http_scripts = self.web_site_script_dependencies[web_site][1]

            if https_scripts is None:
                pass
            else:
                for script in https_scripts:
                    script_site = url_utils.deduct_second_component(script.src)

                    # for script_sites set result
                    script_sites.add(script_site)

                    # for result set
                    try:
                        result[script]
                    except KeyError:
                        result[script] = set()
                    finally:
                        result[script].add(script_site)

            if http_scripts is None:
                pass
            else:
                for script in http_scripts:
                    script_site = url_utils.deduct_second_component(script.src)

                    # for script_sites set result
                    script_sites.add(script_site)

                    # for result set
                    try:
                        result[script]
                    except KeyError:
                        result[script] = set()
                    finally:
                        result[script].add(script_site)
        return result, script_sites

    # TODO: tenere traccia del fatto che il nameserver non ha nessuna delle 2 entry
    @staticmethod
    def _reformat_entries(ip_as_db_entries_result: dict) -> dict:
        """
        This method concern is to re-write the results of the .tsv database elaboration.
        That is necessary because the ROVPageScraper loads an AS page that obviously contains all infos about that AS.
        This page takes lot of time to load.
        If we iterate all the nameservers in the .tsv database result we might come across lots of nameservers that are
        part of the same AS, and so we load the same AS page multiple times! To avoid this we need to 'turn upside down'
        the dictionary and make a new one that has all the AS numbers as keys.
        This method does that.

        :param ip_as_db_entries_result: Dictionary result from the .tsv database resolver.
        :type ip_as_db_entries_result: Dict[str: Tuple[str, EntryIpAsDatabase, ipaddress.IPv4Network]]
        :return: The dictionary 'reformatted': a dictionary with AS number as keys, and as value another dictionary that
        has the nameserver as keys and the same tuple from the original dictionary as value.
        :rtype: Dict[int: Dict[str: List[str or EntryIpAsDatabase or IPv4Network or None]]]
        """
        reformat_dict = dict()
        for nameserver in ip_as_db_entries_result.keys():
            ip_string = ip_as_db_entries_result[nameserver][0]  # str
            entry_ip_as_db = ip_as_db_entries_result[nameserver][1]  # EntryIpAsDatabase
            if entry_ip_as_db is None:
                continue
            belonging_network_ip_as_db = ip_as_db_entries_result[nameserver][2]  # ipaddress.IPv4Network
            try:
                reformat_dict[entry_ip_as_db.as_number]
                try:
                    reformat_dict[entry_ip_as_db.as_number][nameserver]
                except KeyError:
                    reformat_dict[entry_ip_as_db.as_number][nameserver] = [ip_string, entry_ip_as_db,
                                                                                      belonging_network_ip_as_db]
            except KeyError:
                reformat_dict[entry_ip_as_db.as_number] = dict()
                reformat_dict[entry_ip_as_db.as_number][nameserver] = [ip_string, entry_ip_as_db,
                                                                                  belonging_network_ip_as_db]
        return reformat_dict

    @staticmethod
    def merge_current_dict_to_total(total_results_dict: dict, current_results_dict: dict) -> None:
        """
        This method merge the values from a key of a dictionary to another dictionary if absent in the latter.
        The keys/values are not deleted from the original dictionary.

        :param total_results_dict: The dictionary that will be updated.
        :type total_results_dict: dict
        :param current_results_dict: The dictionary from which the keys/values are taken.
        :param current_results_dict: dict
        """
        for key in current_results_dict.keys():
            try:
                total_results_dict[key]
            except KeyError:
                total_results_dict[key] = current_results_dict[key]
