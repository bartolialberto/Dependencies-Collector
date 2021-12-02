import ipaddress
from typing import List
import requests
import selenium
from entities.ContentDependenciesResolver import ContentDependenciesResolver
from entities.DnsResolver import DnsResolver
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.IpAsDatabase import IpAsDatabase
from entities.ROVPageScraper import ROVPageScraper
from entities.error_log.ErrorLog import ErrorLog
from entities.error_log.ErrorLogger import ErrorLogger
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from utils import file_utils, requests_utils, list_utils, domain_name_utils


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
    def __init__(self):
        """
        Initialize all components from scratch.
        Here is checked the presence of the geckodriver executable and the presence of the .tsv database.
        If the latter is absent then automatically it will be downloaded and put in the input folder.

        """
        self._dns_resolver = DnsResolver()
        try:
            self._dns_resolver.cache.load_csv_from_output_folder()
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
            self._ip_as_database = IpAsDatabase()
        except (FileWithExtensionNotFoundError, OSError) as e:
            print(f"!!! {str(e)} !!!")
            exit(1)
        try:
            self._headless_browser = FirefoxHeadlessWebDriver()
        except FileWithExtensionNotFoundError as e:
            print(f"!!! {e.message} !!!")
            exit(1)
        except selenium.common.exceptions.WebDriverException as e:
            print(f"!!! {str(e)} !!!")
            exit(1)
        self._content_resolver = ContentDependenciesResolver(self._headless_browser)
        self._rov_page_scraper = ROVPageScraper(self._headless_browser)
        self._error_logger = ErrorLogger()
        self._total_domain_names = list()
        self._total_dns_results = dict()
        self._total_ip_as_db_results = dict()
        self._total_landing_page_results = dict()
        self._total_content_dependencies_results = dict()
        self._total_rov_page_scraper_results = dict()

    @property
    def dns_resolver(self):
        return self._dns_resolver

    @property
    def ip_as_database(self):
        return self._ip_as_database

    @property
    def headless_browser(self):
        return self._headless_browser

    @property
    def content_resolver(self):
        return self._content_resolver

    @property
    def rov_page_scraper(self):
        return self._rov_page_scraper

    @property
    def error_logger(self):
        return self._error_logger

    @property
    def domain_names(self):
        return self._total_domain_names

    @property
    def dns_results(self):
        return self._total_dns_results

    @property
    def ip_as_db_results(self):
        return self._total_ip_as_db_results

    @property
    def landing_page_results(self):
        return self._total_landing_page_results

    @property
    def content_dependencies_results(self):
        return self._total_content_dependencies_results

    def do_recursive_cycle_execution(self, new_domain_names: List[str]):
        """
        This method concern is to execute the so called recursive cycle as described in the README.md file.
        It starts from the domain names to be checked (the parameter of this method), then in sequence are performed:

        1- DNS Resolver to check zone dependencies.

        2- Network's number database resolver to find an AS associated to every nameserver with a valid IP from the.
        previous component (and a possible belonging network)

        3- Landing page resolver to find a landing page (url) from each domain name from the start of the DNS resolver

        4- Content dependencies resolver to find all the script dependencies from all landing page from previous
        component

        At this point, from all the content dependencies, it extracts all the domain name and compare them to the
        initial domain names: if some domain names are new then the cycle repeats using such new domain names.
        The cycle ends when there aren't new domain names to check.

        :param new_domain_names: A list of domain name.
        :type new_domain_names: List[str]
        :return: Itself
        """
        if len(new_domain_names) == 0:
            print(f"NO NEW DOMAIN NAME.")
            return
        # resolvers elaboration
        current_dns_results = self.do_dns_resolving(new_domain_names)
        current_ip_as_db_results = self.do_ip_as_database_resolving(current_dns_results)
        current_landing_page_results = self.do_landing_page_resolving(new_domain_names)
        current_content_dependencies_results = self.do_content_dependencies_resolving(current_landing_page_results)
        # keeping track of results
        self._merge_current_results_to_total_results(current_dns_results, current_ip_as_db_results, current_landing_page_results, current_content_dependencies_results)
        ApplicationResolvers.merge_current_list_to_total(self._total_domain_names, new_domain_names)
        # control in the content dependencies if there are new names
        self._extract_new_domain_names(new_domain_names, current_content_dependencies_results)      # new_domain_names is overwritten
        # prints
        print(f"")
        for i, new_domain_name in enumerate(new_domain_names):
            print(f"NEW DOMAIN NAME[{i + 1}/{len(new_domain_names)}]: {new_domain_name}")
        return self.do_recursive_cycle_execution(new_domain_names)

    def do_dns_resolving(self, domain_names: List[str]) -> dict:
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
        dns_results = self.dns_resolver.search_multiple_domains_dependencies(domain_names)
        print("END DNS DEPENDENCIES RESOLVER")
        return dns_results

    def do_ip_as_database_resolving(self, dns_results: dict) -> dict:
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
        for index_domain, domain in enumerate(dns_results.keys()):
            print(f"Handling domain[{index_domain}] '{domain}'")
            for index_zone, zone in enumerate(dns_results[domain]):
                print(f"--> Handling zone[{index_zone}] '{zone.name}'")
                for index_rr, rr in enumerate(zone.nameservers):
                    try:
                        ip = ipaddress.IPv4Address(rr.get_first_value())
                        entry = self._ip_as_database.resolve_range(ip)
                        try:
                            belonging_network_ip_as_db, networks = entry.get_network_of_ip(ip)
                            print(
                                f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) found AS{str(entry.as_number)}: [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. Belonging network: {belonging_network_ip_as_db.compressed}")
                            ip_as_db_entries_result[rr.name] = (rr.get_first_value(), entry, belonging_network_ip_as_db)
                        except ValueError as exc:
                            print(
                                f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) found AS record: [{entry}]")
                            self.error_logger.add_entry(ErrorLog(exc, rr.get_first_value(),
                                                                f"Impossible to compute belonging network from AS{str(entry.as_number)} IP range [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]"))
                            ip_as_db_entries_result[rr.name] = (rr.get_first_value(), entry, None)
                    except AutonomousSystemNotFoundError as exc:
                        print(f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) no AS found.")
                        self.error_logger.add_entry(ErrorLog(exc, rr.get_first_value(), f"No AS found in the database."))
                        ip_as_db_entries_result[rr.name] = (None, None, None)  # TODO: tenerne traccia in qualche modo
        print("END IP-AS RESOLVER")
        return ip_as_db_entries_result

    def do_landing_page_resolving(self, domain_name_list: List[str]) -> dict:
        """
        Landing page elaboration. From every domain name an url is constructed and tried to connect with. From the
        request it is saved also the redirection path and the HTTP Strict Transport Security header presence.
        First HTTPS is used, then HTTPS if the connection seems to have trouble.

        :param domain_name_list: A list of domain names.
        :type domain_name_list: List[str]
        :return: The results as a dictionary in which the key is a domain name, and the value is a 3 elements long tuple
        containing: the landing url, the redirection path and the HSTS header presence.
        :rtype: Dict[str: Tuple[str, List[str], bool]]
        """
        print("\n\nSTART LANDING PAGE RESOLVER")
        landing_page_results = dict()
        for domain_name in domain_name_list:
            print(f"\nTrying to connect to domain '{domain_name}' via HTTPS:")
            try:
                (landing_url, redirection_path, hsts) = requests_utils.resolve_landing_page(domain_name)
                print(f"Landing url: {landing_url}")
                print(f"HTTP Strict Transport Security: {hsts}")
                print(f"Redirection path:")
                for index, url in enumerate(redirection_path):
                    print(f"[{index + 1}/{len(redirection_path)}]: {url}")
                landing_page_results[domain_name] = (landing_url, redirection_path, hsts)
            except requests.exceptions.ConnectionError as exc:  # exception that contains the case in which HTTPS is not supported by the server
                try:
                    # TODO: caso in cui c'è una ConnectionError ma non è il caso in cui è supportato solo http... Come si fa?
                    (landing_url, redirection_path, hsts) = requests_utils.resolve_landing_page(domain_name, as_https=False)
                    print(f"It seems that HTTPS is not supported by server. Trying with HTTP:")
                    print(f"Landing url: {landing_url}")
                    print(f"HTTP Strict Transport Security: {hsts}")
                    print(f"Redirection path:")
                    for index, url in enumerate(redirection_path):
                        print(f"[{index + 1}/{len(redirection_path)}]: {url}")
                    landing_page_results[domain_name] = (landing_url, redirection_path, hsts)
                except Exception as exc:  # sono tante!
                    print(f"!!! {str(exc)} !!!")
                    self.error_logger.add_entry(ErrorLog(exc, domain_name, str(exc)))
            except Exception as exc:  # sono tante!
                print(f"!!! {str(exc)} !!!")
                self.error_logger.add_entry(ErrorLog(exc, domain_name, str(exc)))
        print("END LANDING PAGE RESOLVER")
        return landing_page_results

    def do_content_dependencies_resolving(self, landing_page_results: dict) -> dict:
        """
        Content dependencies resolver. From all the results of the previous landing page resolver, this method gets
        all the script dependencies of each url.

        :param landing_page_results: Dictionary from the landing page resolution.
        :type landing_page_results: Dict[str: Tuple[str, List[str], bool]]
        :return: The results as a dictionary in which the key is a landing url, and the value is a list of content
        dependencies.
        :rtype: Dict[str: List[ContentDependencyEntry]]
        """
        print("\n\nSTART CONTENT DEPENDENCIES RESOLVER")
        content_dependencies_result = dict()
        for domain_name in landing_page_results.keys():
            print(f"Searching content dependencies for: {landing_page_results[domain_name][0]}")
            try:
                content_dependencies = self.content_resolver.search_script_application_dependencies(
                    landing_page_results[domain_name][0], ['javascript', 'application/'])
                for index, dep in enumerate(content_dependencies):
                    print(f"--> [{index + 1}]: {str(dep)}")
                content_dependencies_result[landing_page_results[domain_name][0]] = content_dependencies
            except selenium.common.exceptions.WebDriverException as exc:
                print(f"!!! {str(exc)} !!!")
                self.error_logger.add_entry(ErrorLog(exc, landing_page_results[domain_name][0], str(exc)))
        print("END CONTENT DEPENDENCIES RESOLVER")
        return content_dependencies_result

    def do_rov_page_scraping(self) -> dict:
        """
        ROV Page scraping. This method takes all the results of the .tsv database elaboration (saved in the state of
        self object) and scrapes all the AS pages in search of a valid entry in the prefixes table.

        :returns: The results as a dictionary in which the key is an AS number, and the value is a list of 4 elements
        (not a tuple because the elements are mutable). The elements are: the ip as string, the entry of the .tsv
        database, the belonging network computation from the .tsv database or None, the ROVPage entry or None.
        :rtype: Dict[int: Dict[str: List[str or EntryIpAsDatabase or IPv4Network or RowPrefixesTable or None]]]
        """
        print("\n\nSTART ROV PAGE SCRAPING")
        entries_result_by_as = ApplicationResolvers._reformat_entries(self._total_ip_as_db_results)
        for as_number in entries_result_by_as.keys():
            print(f"Loading page for AS{as_number}")
            try:
                self.rov_page_scraper.load_as_page(as_number)
            except selenium.common.exceptions.WebDriverException as exc:
                print(f"!!! {str(exc)} !!!")
                entries_result_by_as[as_number][nameserver].append(None)  # FIXME: anche [nameserver]? Perché?
                self.error_logger.add_entry(ErrorLog(exc, as_number, str(exc)))
                continue
            except ValueError as exc:
                print(f"!!! {str(exc)} !!!")
                entries_result_by_as[as_number][nameserver].append(None)
                self.error_logger.add_entry(ErrorLog(exc, as_number, str(exc)))
                continue
            except selenium.common.exceptions.NoSuchElementException as exc:
                print(f"!!! {str(exc)} !!!")
                entries_result_by_as[as_number][nameserver].append(None)
                self.error_logger.add_entry(ErrorLog(exc, as_number, str(exc)))
                continue
            except TableEmptyError as exc:  # FIXME: differenziare meglio, TableNonExistent e TableEmpty
                print(f"!!! {exc.message} !!!")
                entries_result_by_as[as_number][nameserver].append(None)
                self.error_logger.add_entry(ErrorLog(exc, as_number, str(exc)))
                continue
            except NotROVStateTypeError as exc:
                print(f"!!! {exc.message} !!!")
                entries_result_by_as[as_number][nameserver].append(None)
                self.error_logger.add_entry(ErrorLog(exc, as_number, str(exc)))
                continue
            for nameserver in entries_result_by_as[as_number].keys():
                ip_string = entries_result_by_as[as_number][nameserver][0]
                entry_ip_as_db = entries_result_by_as[as_number][nameserver][1]
                belonging_network_ip_as_db = entries_result_by_as[as_number][nameserver][2]
                try:
                    row = self.rov_page_scraper.get_network_if_present(
                        ipaddress.ip_address(ip_string))  # non gestisco ValueError perché non può accadere qua
                    entries_result_by_as[as_number][nameserver].append(row)
                    print(f"--> for '{nameserver}' ({ip_string}), found row: {str(row)}")
                except TableEmptyError as exc:
                    print(f"!!! {exc.message} !!!")
                    entries_result_by_as[as_number][nameserver].append(None)
                    self.error_logger.add_entry(ErrorLog(exc, ip_string, str(exc)))
                except NetworkNotFoundError as exc:
                    print(f"!!! {exc.message} !!!")
                    entries_result_by_as[as_number][nameserver].append(None)
                    self.error_logger.add_entry(ErrorLog(exc, ip_string, str(exc)))
        print("END ROV PAGE SCRAPING")
        self._total_rov_page_scraper_results = entries_result_by_as
        return entries_result_by_as

    def _extract_new_domain_names(self, current_domain_names: List[str], current_content_dependencies_results: dict) -> None:
        """
        This method checks if are there new domain names from current_content_dependencies_results with respect to the
        current domain names and the total domain names (instance attribute).
        If there are, then then parameter current_domain_names is updated.

        :param current_domain_names: A list of domain names.
        :type current_domain_names: List[str]
        :param current_content_dependencies_results: Results of the content dependencies resolver.
        :type current_content_dependencies_results: Dict[str: List[ContentDependencyEntry]]
        """
        for landing_page in current_content_dependencies_results.keys():
            for entry in current_content_dependencies_results[landing_page]:
                if not domain_name_utils.is_contained_in_list(self._total_domain_names, entry.domain_name): # append with no duplicates watching also the trailing point
                    list_utils.append_with_no_duplicates(current_domain_names, entry.domain_name)

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

    def _merge_current_results_to_total_results(self, current_dns_results: dict, current_ip_as_db_results: dict, current_landing_page_results: dict, current_content_dependencies_results: dict) -> None:
        """
        This method merge the keys/values from all results' dictionaries of each components of the recursive cyle
        to the state of self object (instance attributes).
        The keys/values are not deleted from the original dictionaries.

        :param current_dns_results: Results from the DNS resolver.
        :type current_dns_results: Dict[str: List[Zone]]
        :param current_ip_as_db_results: Results from the .tsv database resolver.
        :type current_ip_as_db_results: Dict[str: Tuple[str, EntryIpAsDatabase or None, ipaddress.IPv4Network or None]]
        :param current_landing_page_results: Results from the landing page resolver.
        :type current_landing_page_results: Dict[str: Tuple[str, List[str], bool]]
        :param current_content_dependencies_results: Results from the landing page resolver.
        :type current_content_dependencies_results: Dict[str: List[ContentDependencyEntry]]
        """
        ApplicationResolvers.merge_current_dict_to_total(self._total_dns_results, current_dns_results)
        ApplicationResolvers.merge_current_dict_to_total(self._total_ip_as_db_results, current_ip_as_db_results)
        ApplicationResolvers.merge_current_dict_to_total(self._total_landing_page_results, current_landing_page_results)
        ApplicationResolvers.merge_current_dict_to_total(self._total_content_dependencies_results, current_content_dependencies_results)

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

    @staticmethod
    def merge_current_list_to_total(total_list: list, current_list: list) -> None:
        """
        This method merge the values from a list to another list if absent in the latter.
        The values in the old list ARE deleted.

        :param total_list: The list that will be updated.
        :type total_list: list
        :param current_list: The list from which the elements are taken.
        :type current_list: list
        """
        for domain_name in current_list:
            list_utils.append_with_no_duplicates(total_list, domain_name)
        for i in range(len(current_list)):
            current_list.pop()
