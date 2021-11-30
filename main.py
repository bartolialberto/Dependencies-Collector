import ipaddress
import sys
from typing import List
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.ROVPageScraper import ROVPageScraper
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from persistence import helper_domain_name, helper_landing_page, helper_content_dependency, helper_matches
from persistence.BaseModel import db
from take_snapshot import take_snapshot
from pathlib import Path
import selenium
from entities.DnsResolver import DnsResolver
from entities.ContentDependenciesResolver import ContentDependenciesResolver
from entities.IpAsDatabase import IpAsDatabase
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import network_utils, list_utils, shell_utils, requests_utils, results_utils, file_utils
from utils import domain_name_utils

# entities
dns_resolver = DnsResolver()
ip_as_db = None
headless_browser = None
try:
    ip_as_db = IpAsDatabase()
except (FileWithExtensionNotFoundError, OSError) as e:
    print(f"!!! {str(e)} !!!")
    exit(1)
try:
    headless_browser = FirefoxHeadlessWebDriver()
except FileWithExtensionNotFoundError as e:
    print(f"!!! {e.message} !!!")
    exit(1)
except selenium.common.exceptions.WebDriverException as e:
    print(f"!!! {str(e)} !!!")
    exit(1)
content_resolver = ContentDependenciesResolver(headless_browser)
rov_page_scraper = ROVPageScraper(headless_browser)


def get_domain_names() -> List[str]:
    domain_name_list = list()
    if len(sys.argv) == 1:
        print(f"> No domain names found in command line.")
        try:
            result = file_utils.search_for_file_type_in_subdirectory("input", ".txt")
        except FileWithExtensionNotFoundError:
            print(f"> No .txt file found in input folder found.")
            print(f"> Starting application with default domain names as sample:")
            domain_name_list.append('google.it')
            domain_name_list.append('youtube.it')
            for index, domain_name in enumerate(domain_name_list):
                print(f"> [{index + 1}/{len(domain_name_list)}]: {domain_name}")
            return domain_name_list
        file = result[0]
        abs_filepath = str(file)
        with open(abs_filepath, 'r') as f:  # 'w' or 'x'
            print(f"> Found file: {abs_filepath}")
            lines = f.readlines()
            for line in lines:
                candidate = line.rstrip()  # strip from whitespaces and EOL (End Of Line)
                if domain_name_utils.is_grammatically_correct(candidate):
                    domain_name_list.append(candidate)
                else:
                    pass
            f.close()
            if len(domain_name_list) == 0:
                print(f"> The .txt file in input folder doesn't contain any valid domain name.")
                exit(0)
    else:
        print('> Argument List:', str(sys.argv))
        for arg in sys.argv[1:]:
            if domain_name_utils.is_grammatically_correct(arg):
                pass
            else:
                print(f"!!! {arg} is not a well-formatted domain name. !!!")
        if len(domain_name_list) == 0:
            print(f"!!! Command line arguments are not well-formatted domain names. !!!")
            exit(1)
        else:
            print(f"> Parsed {len(domain_name_list)} well-formatted domain names:")
            for index, domain_name in enumerate(domain_name_list):
                print(f"> [{index + 1}/{len(domain_name_list)}]: {domain_name}")
    list_utils.remove_duplicates(domain_name_list)
    return domain_name_list


# TODO: tenere traccia del fatto che il nameserver non ha nessuna delle 2 entry
def reformat_entries(ip_as_db_entries_result: dict) -> dict:
    all_entries_result_by_as = dict()
    for nameserver in ip_as_db_entries_result.keys():
        ip_string = ip_as_db_entries_result[nameserver][0]        # str
        entry_ip_as_db = ip_as_db_entries_result[nameserver][1]       # EntryIpAsDatabase
        if entry_ip_as_db is None:
            continue
        belonging_network_ip_as_db = ip_as_db_entries_result[nameserver][2]   # ipaddress.IPv4Network
        try:
            all_entries_result_by_as[entry_ip_as_db.as_number]
            try:
                all_entries_result_by_as[entry_ip_as_db.as_number][nameserver]
            except KeyError:
                all_entries_result_by_as[entry_ip_as_db.as_number][nameserver] = [ip_string, entry_ip_as_db, belonging_network_ip_as_db]
        except KeyError:
            all_entries_result_by_as[entry_ip_as_db.as_number] = dict()
            all_entries_result_by_as[entry_ip_as_db.as_number][nameserver] = [ip_string, entry_ip_as_db, belonging_network_ip_as_db]
    return all_entries_result_by_as


def dns_resolving(domain_names: List[str]) -> dict:
    print("\n\nSTART DNS DEPENDENCIES RESOLVER")
    dns_resolver.cache.take_snapshot()
    dns_results = dns_resolver.search_multiple_domains_dependencies(domain_names)
    print("END DNS DEPENDENCIES RESOLVER")
    return dns_results


def ip_as_resolving(dns_results: dict) -> dict:
    print("\n\nSTART IP-AS RESOLVER")
    ip_as_db_entries_result = dict()
    for index_domain, domain in enumerate(dns_results.keys()):
        print(f"Handling domain[{index_domain}] '{domain}'")
        for index_zone, zone in enumerate(dns_results[domain]):
            print(f"--> Handling zone[{index_zone}] '{zone.name}'")
            for index_rr, rr in enumerate(zone.nameservers):
                try:
                    ip = ipaddress.IPv4Address(rr.get_first_value())
                    entry = ip_as_db.resolve_range(ip)
                    try:
                        belonging_network_ip_as_db, networks = entry.get_network_of_ip(ip)
                        print(f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) found AS{str(entry.as_number)}: [{entry.start_ip_range.compressed} - {entry.end_ip_range.compressed}]. Belonging network: {belonging_network_ip_as_db.compressed}")
                        ip_as_db_entries_result[rr.name] = (rr.get_first_value(), entry, belonging_network_ip_as_db)
                    except ValueError:
                        print(f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) found AS record: [{entry}]")
                        ip_as_db_entries_result[rr.name] = (rr.get_first_value(), entry, None)
                except AutonomousSystemNotFoundError:
                    print(f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) no AS found.")
                    ip_as_db_entries_result[rr.name] = (None, None, None)      # TODO: tenerne traccia in qualche modo
    print("END IP-AS RESOLVER")
    return ip_as_db_entries_result


def landing_page_resolving(domain_name_list: List[str]) -> dict:
    print("\n\nSTART LANDING PAGE RESOLVER")
    landing_page_results = dict()
    for domain_name in domain_name_list:
        print(f"\nTrying to connect to domain '{domain_name}' via https:")
        try:
            (landing_url, redirection_path, hsts) = requests_utils.resolve_landing_page(domain_name)
            print(f"Landing url: {landing_url}")
            print(f"HTTP Strict Transport Security: {hsts}")
            print(f"Redirection path:")
            for index, url in enumerate(redirection_path):
                print(f"[{index + 1}/{len(redirection_path)}]: {url}")
            landing_page_results[domain_name] = (landing_url, redirection_path, hsts)
        except Exception as exc:    # sono tante!
            print(f"!!! {str(exc)} !!!")
    print("END LANDING PAGE RESOLVER")
    return landing_page_results


def content_resolving(landing_page_results: dict) -> dict:
    print("\n\nSTART CONTENT DEPENDENCIES RESOLVER")
    content_dependencies_result = dict()
    for domain_name in landing_page_results.keys():
        print(f"Searching content dependencies for: {landing_page_results[domain_name][0]}")
        try:
            content_dependencies = content_resolver.search_script_application_dependencies(landing_page_results[domain_name][0], ['javascript', 'application/'])
            for index, dep in enumerate(content_dependencies):
                print(f"--> [{index+1}]: {str(dep)}")
            content_dependencies_result[landing_page_results[domain_name][0]] = content_dependencies
        except selenium.common.exceptions.WebDriverException as exc:
            print(f"!!! {str(exc)} !!!")
    print("END CONTENT DEPENDENCIES RESOLVER")
    return content_dependencies_result


def rov_page_scraping(ip_as_db_entries_result) -> dict:
    print("\n\nSTART ROV PAGE SCRAPING")
    all_entries_result_by_as = reformat_entries(ip_as_db_entries_result)
    for as_number in all_entries_result_by_as.keys():
        print(f"Loading page for AS{as_number}")
        try:
            rov_page_scraper.load_as_page(as_number)
        except selenium.common.exceptions.WebDriverException as exc:
            print(f"!!! {str(exc)} !!!")
            all_entries_result_by_as[as_number][nameserver].append(None)
            continue
        except ValueError as exc:
            print(f"!!! {str(exc)} !!!")
            all_entries_result_by_as[as_number][nameserver].append(None)
            continue
        except selenium.common.exceptions.NoSuchElementException as exc:
            print(f"!!! {str(exc)} !!!")
            all_entries_result_by_as[as_number][nameserver].append(None)
            continue
        except TableEmptyError as exc:
            print(f"!!! {exc.message} !!!")
            all_entries_result_by_as[as_number][nameserver].append(None)
            continue
        except NotROVStateTypeError as exc:
            print(f"!!! {exc.message} !!!")
            all_entries_result_by_as[as_number][nameserver].append(None)
            continue
        for nameserver in all_entries_result_by_as[as_number].keys():
            ip_string = all_entries_result_by_as[as_number][nameserver][0]
            entry_ip_as_db = all_entries_result_by_as[as_number][nameserver][1]
            belonging_network_ip_as_db = all_entries_result_by_as[as_number][nameserver][2]
            try:
                row = rov_page_scraper.get_network_if_present(ipaddress.ip_address(ip_string))
                all_entries_result_by_as[as_number][nameserver].append(row)
                print(f"--> for '{nameserver}' ({ip_string}), found row: {str(row)}")
            except TableEmptyError as exc:
                print(f"!!! {exc.message} !!!")
                all_entries_result_by_as[as_number][nameserver].append(None)
            except NetworkNotFoundError as exc:
                print(f"!!! {exc.message} !!!")
                all_entries_result_by_as[as_number][nameserver].append(None)
    print("END ROV PAGE SCRAPING")
    return all_entries_result_by_as


def do_recursive_execution(new_domain_names: List[str], total_domain_names: List[str], total_dns_results: dict, total_ip_as_results: dict, total_landing_page_results: dict, total_content_dependencies_result: dict):
    if len(new_domain_names) == 0:
        print(f"NO NEW DOMAIN NAME.")
        return
    new_dns_results = dns_resolving(new_domain_names)
    results_utils.merge_dns_results(total_dns_results, new_dns_results)
    new_ip_as_results = ip_as_resolving(new_dns_results)
    results_utils.merge_ip_as_db_results(total_ip_as_results, new_ip_as_results)
    new_landing_page_results = landing_page_resolving(new_domain_names)
    results_utils.merge_landing_page_results(total_landing_page_results, new_landing_page_results)
    new_content_dependencies_results = content_resolving(new_landing_page_results)
    results_utils.merge_content_dependencies_results(total_content_dependencies_result, new_content_dependencies_results)
    # copy every new name in the total list
    for domain_name in new_domain_names:
        list_utils.append_with_no_duplicates(total_domain_names, domain_name)
    for i in range(len(new_domain_names)):
        new_domain_names.pop()
    # control in the content dependencies if there are new names
    for landing_page in new_content_dependencies_results.keys():
        for entry in new_content_dependencies_results[landing_page]:
            # append with no duplicates watching also the trailing point
            if not domain_name_utils.is_contained_in_list(total_domain_names, entry.domain_name):
                list_utils.append_with_no_duplicates(new_domain_names, entry.domain_name)
    print(f"")
    for i, new_domain_name in enumerate(new_domain_names):
        print(f"NEW DOMAIN NAME[{i+1}/{len(new_domain_names)}]: {new_domain_name}")
    return do_recursive_execution(new_domain_names, total_domain_names, total_dns_results, total_ip_as_results, total_landing_page_results, total_content_dependencies_result)


def application_runner():
    print(f"Local IP: {network_utils.get_local_ip()}")
    print(f"Current working directory ( Path.cwd() ): {Path.cwd()}")
    # input
    total_domain_names = list()
    new_domain_names = get_domain_names()
    domain_name_utils.take_snapshot(new_domain_names)
    try:
        dns_resolver.cache.load_csv_from_output_folder()
    except (ValueError, FilenameNotFoundError, OSError) as exc:
        print(f"!!! {str(exc)} !!!")
    # component's results that will be populated
    total_dns_results = dict()
    total_ip_as_results = dict()
    total_landing_page_results = dict()
    total_content_dependencies_result = dict()
    tsv_db_is_updated = file_utils.is_tsv_database_updated()
    if tsv_db_is_updated:
        print("> .tsv database file is updated.")
    else:
        print("> Latest .tsv database (~25 MB) is downloading and extracting... ", end='')
        requests_utils.download_latest_tsv_database()
        print("DONE.")
    # actual elaboration
    do_recursive_execution(new_domain_names, total_domain_names, total_dns_results, total_ip_as_results, total_landing_page_results, total_content_dependencies_result)
    # rov scraping is done outside the recursive cycle
    total_entries_result_by_as = rov_page_scraping(total_ip_as_results)
    print("Insertion into database... ", end='')
    helper_domain_name.multiple_inserts(total_dns_results)
    helper_landing_page.multiple_inserts(total_landing_page_results)
    helper_content_dependency.multiple_inserts(total_content_dependencies_result)
    helper_matches.insert_all_entries_associated(total_entries_result_by_as)
    print("DONE.")
    # export
    dns_resolver.cache.write_to_csv_in_output_folder()
    dns_resolver.error_logs.write_to_csv_in_output_folder()
    # closing
    headless_browser.close()
    db.close()


if __name__ == "__main__":
    print("********** START APPLICATION **********")
    try:
        application_runner()
    except Exception as e:
        take_snapshot(e)
        headless_browser.close()
        print(f"!!! Unexpected exception occurred. SNAPSHOT taken. !!!")
        print(f"!!! {str(e)} !!!")
    print("********** APPLICATION END **********")
