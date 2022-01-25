import ipaddress
from typing import List, Dict, Tuple, Set
import selenium

from entities.enums.ServerTypes import ServerTypes
from entities.resolvers.ScriptDependenciesResolver import ScriptDependenciesResolver, MainPageScript
from entities.resolvers.DnsResolver import DnsResolver
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.resolvers.IpAsDatabase import IpAsDatabase
from entities.resolvers.LandingResolver import LandingResolver
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from entities.resolvers.results.AutonomousSystemResolutionResults import AutonomousSystemResolutionResults
from entities.resolvers.results.LandingSiteResult import LandingSiteResult
from entities.resolvers.results.MultipleDnsMailServerDependenciesResult import MultipleDnsMailServerDependenciesResult
from entities.resolvers.results.MultipleDnsZoneDependenciesResult import MultipleDnsZoneDependenciesResult
from entities.resolvers.results.ScriptDependenciesResult import ScriptDependenciesResult
from entities.scrapers.ROVPageScraper import ROVPageScraper
from entities.scrapers.TLDPageScraper import TLDPageScraper
from entities.Zone import Zone
from entities.error_log.ErrorLog import ErrorLog
from entities.error_log.ErrorLogger import ErrorLogger
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.InvalidUrlError import InvalidUrlError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError
from utils import file_utils, requests_utils, list_utils, domain_name_utils, url_utils


class ApplicationResolversWrapper:
    """
    This class represents the resolvers of the application all in one. Thanks to this it can track and handle all the
    results of each component and save all of them as object state (instance attributes).

    ...

    Attributes
    ----------
    landing_resolver : LandingResolver
        Instance of a LandingResolver object.
    headless_browser : FirefoxHeadlessWebDriver
        Instance of a FirefoxHeadlessWebDriver object.
    _tld_scraper : TLDPageScraper or None
        Instance of a TLDPageScraper object or None.
    dns_resolver : DnsResolver
        Instance of a DnsResolver object.
    ip_as_database : IpAsDatabase
        Instance of a IpAsDatabase object.
    script_resolver : ScriptDependenciesResolver
        Instance of a ScriptDependenciesResolver object.
    rov_page_scraper : ROVPageScraper
        Instance of a ROVPageScraper object.
    error_logger : ErrorLogger
        Instance of a ErrorLogger object.
    landing_web_sites_results : Dict[str, LandingSiteResult]
        Dictionary of results from web sites landing resolving.
    landing_script_sites_results : Dict[str, LandingSiteResult]
        Dictionary of results from script sites landing resolving.
    web_site_script_dependencies : Dict[str, ScriptDependenciesResult]
        Dictionary of results from script dependencies of web sites.
    script_script_site_dependencies : Tuple[Dict[MainPageScript, Set[str]], Set[str]]
        Tuple containing a dictionary for script-script site association and a set of all scrip sites.
    mail_domains_results : Tuple[Dict[str, List[str]], List[ErrorLog]]
        Tuple containing a dictionary for mail domain-mail servers association and a list or errors occurred.
    total_dns_results : Dict[str, List[Zone]]
        Dictionary of entire results from DNS resolving of mail domain zone dependencies.
    total_ip_as_db_results : AutonomousSystemResolutionResults
        Results from IpAsDatabase resolving.
    total_rov_page_scraper_results : ASResolverResultForROVPageScraping
        Results for and from ROVPage scraping.
    """
    def __init__(self, consider_tld=False):
        """
        Initialize all components from scratch.
        Here is checked the presence of the geckodriver executable and the presence of the .tsv database.
        If the latter is absent then automatically it will be downloaded and put in the input folder.
        If the consider_flag flag is true then a TLDPageScraper is instantiated and the TLDs list is computed.

        :param consider_tld: A flag that will consider or remove the Top-Level Domains when computing zone dependencies.
        :type consider_tld: bool
        """
        try:
            self.headless_browser = FirefoxHeadlessWebDriver()
        except (FileWithExtensionNotFoundError, selenium.common.exceptions.WebDriverException) as e:
            print(f"!!! {str(e)} !!!")
            raise Exception
        if not consider_tld:
            self._tld_scraper = TLDPageScraper(self.headless_browser)
            try:
                tlds = self._tld_scraper.scrape_tld()
            except (selenium.common.exceptions.WebDriverException, selenium.common.exceptions.NoSuchElementException) as e:
                print(f"!!! {str(e)} !!!")
                raise Exception
            print(f"> TLDs scraping completed. {len(tlds)} TLDs parsed.")
        else:
            print(f"> No TLDs scraping executed.")
            self._tld_scraper = None
            tlds = None
        self.dns_resolver = DnsResolver(tlds)
        self.landing_resolver = LandingResolver(self.dns_resolver)
        try:
            self.dns_resolver.cache.load_csv_from_output_folder()
        except (ValueError, FilenameNotFoundError, OSError) as exc:
            print(f"!!! {str(exc)} !!!")
        tsv_db_is_updated = file_utils.is_tsv_database_updated()
        if tsv_db_is_updated:
            print("> .tsv database file is up-to-date.")
        else:
            print("> Latest .tsv database (~25 MB) is downloading and extracting... ", end='')
            requests_utils.download_latest_tsv_database()
            print("DONE.")
        try:
            self.ip_as_database = IpAsDatabase()
        except (FileWithExtensionNotFoundError, OSError) as e:
            print(f"!!! {str(e)} !!!")
            raise Exception
        self.script_resolver = ScriptDependenciesResolver(self.headless_browser)
        self.rov_page_scraper = ROVPageScraper(self.headless_browser)
        self.error_logger = ErrorLogger()
        # results
        self.landing_web_sites_results = dict()
        self.landing_script_sites_results = dict()
        self.web_site_script_dependencies = dict()
        self.script_script_site_dependencies = tuple()
        self.mail_domains_results = MultipleDnsMailServerDependenciesResult()
        self.total_dns_results = MultipleDnsZoneDependenciesResult()
        self.total_ip_as_db_results = AutonomousSystemResolutionResults()
        self.total_rov_page_scraper_results = None

    def do_preamble_execution(self, web_sites: List[str], mail_domains: List[str]) -> List[str]:
        """
        This method executes the first part of the application named: PREAMBLE.
        The results are saved in the attributes of this object.

        :param web_sites: A list of web sites.
        :type web_sites: List[str]
        :param mail_domains: A list of mail domains.
        :type mail_domains: List[str]
        :return: A list of domain names extracted from the execution.
        :rtype: List[str]
        """
        self.landing_web_sites_results = self.do_web_site_landing_resolving(set(web_sites))
        self.mail_domains_results = self.do_mail_servers_resolving(mail_domains)
        return self._extract_domain_names_from_preamble(mail_domains)

    def do_midst_execution(self, domain_names: List[str]) -> List[str]:
        """
        This method executes the second part of the application named: MIDST.
        The results are saved in the attributes of this object.

        :param domain_names: A list of web sites.
        :type domain_names: List[str]
        :return: A list of domain names extracted from the execution.
        :rtype: List[str]
        """
        current_dns_results = self.do_dns_resolving(domain_names)
        current_ip_as_db_results = self.do_ip_as_database_resolving(current_dns_results, self.landing_web_sites_results, ServerTypes.WEBSERVER)
        self.web_site_script_dependencies = self.do_script_dependencies_resolving()

        # extracting
        self.script_script_site_dependencies, script_sites = self._extract_script_hosting_dependencies()

        self.landing_script_sites_results = self.do_script_site_landing_resolving(script_sites)

        # merging
        self.total_dns_results.merge(current_dns_results)
        self.total_ip_as_db_results.merge(current_ip_as_db_results)

        return self._extract_domain_names_from_landing_script_sites_results()

    def do_epilogue_execution(self, domain_names: List[str]) -> None:
        """
        This method executes the third and last part of the application named: EPILOGUE.
        The results are saved in the attributes of this object.

        :param domain_names: A list of web sites.
        :type domain_names: List[str]
        """
        current_dns_results = self.do_dns_resolving(domain_names)
        current_ip_as_db_results = self.do_ip_as_database_resolving(current_dns_results, self.landing_script_sites_results,  ServerTypes.SCRIPTSERVER)

        # merging results
        self.total_dns_results.merge(current_dns_results)
        self.total_ip_as_db_results.merge(current_ip_as_db_results)

        reformat = ASResolverResultForROVPageScraping(self.total_ip_as_db_results)

        self.total_rov_page_scraper_results = self.do_rov_page_scraping(reformat)

    def do_web_site_landing_resolving(self, web_sites: Set[str]) -> Dict[str, LandingSiteResult]:
        """
        This method executes landing resolving of a set of web sites.

        :param web_sites: A set of web sites.
        :type web_sites: Set[str]
        :return: The landing results.
        :rtype: Dict[str, LandingSiteResult]
        """
        print("\n\nSTART WEB SITE LANDING RESOLVER")
        results = self.landing_resolver.resolve_sites(web_sites)
        for web_site in results.keys():
            self.error_logger.add_entries(results[web_site].error_logs)
        print("END WEB SITE LANDING RESOLVER")
        return results

    def do_script_site_landing_resolving(self, script_sites: Set[str]) -> Dict[str, LandingSiteResult]:
        """
        This method executes landing resolving of a set of script sites.

        :param script_sites: A set of script sites.
        :type script_sites: Set[str]
        :return: The landing results.
        :rtype: Dict[str, LandingSiteResult]
        """
        print("\n\nSTART SCRIPT SITE LANDING RESOLVER")
        results = self.landing_resolver.resolve_sites(script_sites)
        for script_site in results.keys():
            self.error_logger.add_entries(results[script_site].error_logs)
        print("END SCRIPT SITE LANDING RESOLVER")
        return results

    def do_mail_servers_resolving(self, mail_domains: List[str]) -> MultipleDnsMailServerDependenciesResult:
        """
        This method executes mail servers resolving of a list of mail domains.

        :param mail_domains: A list of mail domains.
        :type mail_domains: List[str]
        :return: The resolving results.
        :rtype: MultipleDnsMailServerDependenciesResult
        """
        print("\n\nSTART MAIL DOMAINS RESOLVER")
        results = self.dns_resolver.resolve_multiple_mail_domains(mail_domains)
        self.error_logger.add_entries(results.error_logs)
        print("END MAIL DOMAINS RESOLVER")
        return results

    def do_dns_resolving(self, domain_names: List[str]) -> MultipleDnsZoneDependenciesResult:
        """
        This method executes DNS resolving of a list of domain names.

        :param domain_names: A list of domain names.
        :type domain_names: List[str]
        :return: The resolving results.
        :rtype: MultipleDnsZoneDependenciesResult
        """
        print("\n\nSTART DNS DEPENDENCIES RESOLVER")
        self.dns_resolver.cache.take_temp_snapshot()
        results = self.dns_resolver.resolve_multiple_domains_dependencies(domain_names)
        self.error_logger.add_entries(results.error_logs)
        print("END DNS DEPENDENCIES RESOLVER")
        return results

    def do_ip_as_database_resolving(self, dns_results: MultipleDnsZoneDependenciesResult, landing_results: Dict[str, LandingSiteResult], landing_site_type: ServerTypes) -> AutonomousSystemResolutionResults:
        """
        This method executes IP-AS resolving from the DNS resolving results.

        :param dns_results: The DNS resolving result.
        :type dns_results: MultipleDnsZoneDependenciesResult
        :return: The resolving results.
        :rtype: AutonomousSystemResolutionResults
        """
        print("\n\nSTART IP-AS RESOLVER")
        results = AutonomousSystemResolutionResults()
        for index_domain, domain in enumerate(dns_results.zone_dependencies_per_domain_name.keys()):
            print(f"Handling domain[{index_domain}]: {domain}")
            for index_zone, zone in enumerate(dns_results.zone_dependencies_per_domain_name[domain]):
                print(f"--> Handling zone[{index_zone}]: {zone.name}")
                for i, nameserver in enumerate(zone.nameservers):
                    try:
                        rr_a = zone.resolve_name_server_access_path(nameserver)
                    except NoAvailablePathError:
                        print(f"!!! NO RESOLVED IP ADDRESS FROM name server: {nameserver} !!!")
                        results.add_unresolved_server(nameserver, ServerTypes.NAMESERVER)
                        continue        # should never happen...
                    for ip_string in rr_a.values:
                        ip = ipaddress.IPv4Address(ip_string)        # no exception catch needed
                        try:
                            entry = self.ip_as_database.resolve_range(ip)
                        except (AutonomousSystemNotFoundError, ValueError) as e:
                            results.add_no_as_result(ip, nameserver, ServerTypes.NAMESERVER)
                            print(f"!!! {str(e)} !!!")
                            continue
                        try:
                            ip_range_tsv, networks = entry.get_network_of_ip(ip)
                            print(f"----> for {ip.compressed} ({nameserver}) found AS{str(entry.as_number)}: [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. IP range tsv: {ip_range_tsv.compressed}")
                            results.add_complete_result(ip, nameserver, ServerTypes.NAMESERVER, entry, ip_range_tsv)
                        except ValueError as exc:
                            print(f"----> for {ip.compressed} ({nameserver}) found AS record: [{str(entry)}]")
                            self.error_logger.add_entry(ErrorLog(exc, ip.compressed, f"Impossible to compute belonging network from AS{str(entry.as_number)} IP range [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]"))
                            results.add_no_ip_range_tsv_result(ip, nameserver, ServerTypes.NAMESERVER, entry)
        print()
        for i, site in enumerate(landing_results.keys()):
            print(f"Handling site[{i+1}/{len(landing_results.keys())}]: {site}")
            https_result = landing_results[site].https
            http_result = landing_results[site].http
            if https_result is not None:
                for ip in https_result.ips:
                    try:
                        entry = self.ip_as_database.resolve_range(ip)
                        try:
                            ip_range_tsv, networks = entry.get_network_of_ip(ip)
                            print(
                                f"----> for {ip.compressed} [HTTPS] ({https_result.server}) found AS{str(entry.as_number)}: [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. IP range tsv: {ip_range_tsv.compressed}")
                            results.add_complete_result(ip, https_result.server, landing_site_type, entry, ip_range_tsv)
                        except ValueError as exc:
                            print(f"----> for {ip.compressed} [HTTPS] ({https_result.server}) found AS record: [{str(entry)}]")
                            self.error_logger.add_entry(ErrorLog(exc, ip.exploded, str(exc)))
                            results.add_no_ip_range_tsv_result(ip, https_result.server, landing_site_type, entry)
                    except AutonomousSystemNotFoundError as e:
                        self.error_logger.add_entry(ErrorLog(e, ip.exploded, str(e)))
                        results.add_no_as_result(ip, https_result.server, landing_site_type)
                        print(f"----> for {ip.compressed} [HTTPS] ({https_result.server}) no AS found")
            else:
                print(f"--> [HTTPS] didn't land anywhere.")
            if http_result is not None:
                for ip in http_result.ips:
                    try:
                        entry = self.ip_as_database.resolve_range(ip)
                        try:
                            ip_range_tsv, networks = entry.get_network_of_ip(ip)
                            print(f"----> for {ip.compressed} [HTTP] ({http_result.server}) found AS{str(entry.as_number)}: [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. IP range tsv: {ip_range_tsv.compressed}")
                            results.add_complete_result(ip, http_result.server, landing_site_type, entry, ip_range_tsv)
                        except ValueError as exc:
                            print(f"----> for {ip.compressed} [HTTP] ({http_result.server}) found AS record: [{str(entry)}]")
                            self.error_logger.add_entry(ErrorLog(exc, ip.exploded, str(exc)))
                            results.add_no_ip_range_tsv_result(ip, http_result.server, landing_site_type, entry)
                    except AutonomousSystemNotFoundError as e:
                        self.error_logger.add_entry(ErrorLog(e, ip.exploded, str(e)))
                        results.add_no_as_result(ip, http_result.server, landing_site_type)
                        print(f"----> for {ip.compressed} [HTTP] ({http_result.server}) no AS found")
            else:
                print(f"--> [HTTP] didn't land anywhere.")
        print("END IP-AS RESOLVER")
        return results

    def do_script_dependencies_resolving(self) -> Dict[str, ScriptDependenciesResult]:
        """
        This method executes web sites script dependencies resolving.
        It takes the landing web site resolution results saved in this object.

        :return: The resolving results.
        :rtype: Dict[str, ScriptDependenciesResult]
        """
        print("\n\nSTART SCRIPT DEPENDENCIES RESOLVER")
        script_dependencies_result = dict()
        for website in self.landing_web_sites_results.keys():
            print(f"Searching script dependencies for website: {website}")
            https_result = self.landing_web_sites_results[website].https
            http_result = self.landing_web_sites_results[website].http

            if https_result is None and http_result is None:
                print(f"!!! Neither HTTPS nor HTTP landing possible for: {website} !!!")
                script_dependencies_result[website] = ScriptDependenciesResult(None, None)
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
                    script_dependencies_result[website] = ScriptDependenciesResult(None, http_scripts)
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
                    script_dependencies_result[website] = ScriptDependenciesResult(https_scripts, None)
                except selenium.common.exceptions.WebDriverException as e:
                    print(f"!!! {str(e)} !!!")
                    https_scripts = None
                    self.error_logger.add_entry(ErrorLog(e, https_landing_page, str(e)))
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
                script_dependencies_result[website] = ScriptDependenciesResult(https_scripts, http_scripts)
            print('')
        print("END SCRIPT DEPENDENCIES RESOLVER")
        return script_dependencies_result

    def do_rov_page_scraping(self, reformat: ASResolverResultForROVPageScraping) -> ASResolverResultForROVPageScraping:
        """
        This method executes the ROVPage scraping from the IpAsDatabase resolution results (reformatted).

        :param reformat: A ASResolverResultForROVPageScraping object.
        :type reformat: ASResolverResultForROVPageScraping
        :return: The ASResolverResultForROVPageScraping parameter object updated with new informations.
        :rtype: ASResolverResultForROVPageScraping
        """
        print("\n\nSTART ROV PAGE SCRAPING")
        for as_number in reformat.results.keys():
            print(f"Loading page for AS{as_number}")
            try:
                self.rov_page_scraper.load_as_page(as_number)
            except (TableNotPresentError, ValueError, TableEmptyError, NotROVStateTypeError, selenium.common.exceptions.WebDriverException) as exc:
                print(f"!!! {str(exc)} !!!")
                for ip_address in reformat.results[as_number].keys():
                    reformat.results[as_number][ip_address].insert_rov_entry(None)      # TODO: dovrebbero essere diversi
                self.error_logger.add_entry(ErrorLog(exc, "AS"+str(as_number), str(exc)))
                continue
            for ip_address in reformat.results[as_number].keys():
                server = reformat.results[as_number][ip_address].server
                server_type = reformat.results[as_number][ip_address].server_type
                try:
                    row = self.rov_page_scraper.get_network_if_present(ipaddress.ip_address(ip_address))  # non gestisco ValueError perché non può accadere qua
                    reformat.results[as_number][ip_address].insert_rov_entry(row)
                    print(f"--> for {ip_address} ({server_type.to_string()}: {server}) found row: {str(row)}")
                except (TableNotPresentError, TableEmptyError, NetworkNotFoundError) as exc:
                    print(f"!!! {str(exc)} !!!")
                    reformat.results[as_number][ip_address].insert_rov_entry(None)      # TODO: dovrebbero essere diversi
                    self.error_logger.add_entry(ErrorLog(exc, server, str(exc)))
        print("END ROV PAGE SCRAPING")
        return reformat

    def _extract_domain_names_from_preamble(self, mail_domains: List[str]) -> List[str]:
        """
        This method extract domain names from the PREAMBLE execution: this means it extract them from the landing web
        sites resolution results (saved in this object), and from the input mail domains.

        :param mail_domains: The input mail domains.
        :type mail_domains: List[str]
        :return: A list of extracted domain names.
        :rtype: List[str]
        """
        domain_names = list()
        # adding domain names from webservers and websites
        for website in self.landing_web_sites_results.keys():
            web_site_domain_name = domain_name_utils.deduct_domain_name(website, with_trailing_point=True)
            list_utils.append_with_no_duplicates(domain_names, web_site_domain_name)
            # from web servers
            https_result = self.landing_web_sites_results[website].https
            http_result = self.landing_web_sites_results[website].http
            if https_result is not None:
                list_utils.append_with_no_duplicates(domain_names, https_result.server)
            if http_result is not None:
                list_utils.append_with_no_duplicates(domain_names, http_result.server)
        # adding domain names from mail_domains
        for mail_domain in mail_domains:
            list_utils.append_with_no_duplicates(domain_names, mail_domain)
        return domain_names

    def _extract_domain_names_from_landing_script_sites_results(self) -> List[str]:
        """
        This method extracts domain names from the landing script site resolution results (saved in this object state).

        :return: A list of extracted domain names.
        :rtype: List[str]
        """
        domain_names = list()
        for script_site in self.landing_script_sites_results.keys():
            https_result = self.landing_script_sites_results[script_site].https
            if https_result is not None:
                list_utils.append_with_no_duplicates(domain_names, domain_name_utils.deduct_domain_name(https_result.server, with_trailing_point=True))
            http_result = self.landing_script_sites_results[script_site].http
            if http_result is not None:
                list_utils.append_with_no_duplicates(domain_names, domain_name_utils.deduct_domain_name(http_result.server, with_trailing_point=True))
        return domain_names

    def _extract_script_hosting_dependencies(self) -> Tuple[Dict[MainPageScript, Set[str]], Set[str]]:
        """
        This method extracts the hosting association from each script.
        It means it extracts script sites from scripts and the binding between such script and such script sites.

        :return: A dictionary that associates each script with every script site, and a set of all the script sites.
        Everything wrapped in a tuple.
        :rtype: Tuple[Dict[MainPageScript, Set[str]], Set[str]]
        """
        result = dict()
        script_sites = set()
        for web_site in self.web_site_script_dependencies.keys():
            https_scripts = self.web_site_script_dependencies[web_site].https
            http_scripts = self.web_site_script_dependencies[web_site].http

            if https_scripts is None:
                pass
            else:
                for script in https_scripts:
                    try:
                        script_site = url_utils.deduct_second_component(script.src)
                    except InvalidUrlError:
                        continue

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
                    try:
                        script_site = url_utils.deduct_second_component(script.src)
                    except InvalidUrlError:
                        continue

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
