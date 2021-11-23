import ipaddress
import sys
from entities.FirefoxHeadlessWebDriver import FirefoxHeadlessWebDriver
from entities.ROVPageScraper import ROVPageScraper
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from persistence import helper_domain_name, helper_landing_page, helper_content_dependency, \
    helper_entry_ip_as_database, helper_ip_network, helper_nameserver, helper_matches, \
    helper_belonging_network, helper_entry_rov_page, helper_prefix
from take_snapshot import take_snapshot
from pathlib import Path
import selenium
from entities.DnsResolver import DnsResolver
from entities.ContentDependenciesResolver import ContentDependenciesResolver
from entities.IpAsDatabase import IpAsDatabase
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from exceptions.GeckoDriverExecutableNotFoundError import GeckoDriverExecutableNotFoundError
from exceptions.NoValidDomainNamesFoundError import NoValidDomainNamesFoundError
from utils import network_utils, list_utils, shell_utils, requests_utils
from utils import domain_name_utils


def application_runner():
    print(f"Local IP: {network_utils.get_local_ip()}")
    print(f"Current working directory ( Path.cwd() ): {Path.cwd()}")


    # Getting the domain list in one of the 3 possible ways: through command line, file or by hand.
    domain_name_list = list()
    if len(sys.argv) == 1:
        answer = shell_utils.wait_how_to_load_domain_names_response()
        if answer == 0:
            try:
                domain_name_list = shell_utils.handle_getting_domain_names_from_txt_file()
                print(f"> Parsed {len(domain_name_list)} well-formatted domain names:")
                for index, domain_name in enumerate(domain_name_list):
                    print(f"> [{index + 1}/{len(domain_name_list)}]: {domain_name}")
            except FileWithExtensionNotFoundError:
                print(f"!!! No .txt file found in input folder. !!!")
                exit(1)
            except NoValidDomainNamesFoundError as exc:
                print(f"!!! {exc.message} !!!")
                exit(1)
        else:
            domain_name_list = shell_utils.wait_domain_names_typing()
            print(f"> Parsed {len(domain_name_list)} well-formatted domain names:")
            for index, domain_name in enumerate(domain_name_list):
                print(f"> [{index + 1}/{len(domain_name_list)}]: {domain_name}")
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
    domain_name_utils.take_snapshot(domain_name_list)

    # Starting the actual application
    # DNS DEPENDENCIES RESOLVER
    print("\n\nSTART DNS DEPENDENCIES RESOLVER")
    dns_resolver = DnsResolver()
    try:
        dns_resolver.cache.load_csv_from_output_folder()
    except (ValueError, FilenameNotFoundError, OSError) as exc:
        print(f"!!! {str(exc)} !!!")
    dns_resolver.cache.take_snapshot()
    dns_results = dns_resolver.search_multiple_domains_dependencies(domain_name_list)
    # export
    dns_resolver.cache.write_to_csv_in_output_folder()
    dns_resolver.error_logs.write_to_csv_in_output_folder()
    print("Insertion into database... ", end='')
    helper_domain_name.multiple_inserts(dns_results)
    print("DONE.")
    print("END DNS DEPENDENCIES RESOLVER")

    print("\n\nSTART IP-AS RESOLVER")
    print(f"> Do you want to download latest ip-as database from https://iptoasn.com/ ?")
    answer = shell_utils.wait_yes_or_no_response("> ")
    if answer == 'y' or answer == 'Y':
        print("Latest database is downloading and extracting... ", end='')
        try:
            requests_utils.download_latest_tsv_database()
            print("DONE.")
        except FileWithExtensionNotFoundError as err:
            print(f"!!! {str(err)} !!!")
    else:
        pass
    try:
        ip_as_db = IpAsDatabase()
    except (FileWithExtensionNotFoundError, OSError) as exc:
        print(f"!!! {str(exc)} !!!")
        exit(1)
    entries_result = dict()
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
                        entries_result[rr.name] = rr.get_first_value(), entry, belonging_network_ip_as_db
                    except ValueError:
                        print(f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) found AS record: [{entry}]")
                        entries_result[rr.name] = rr.get_first_value(), entry, None
                except AutonomousSystemNotFoundError:
                    print(f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) no AS found.")
                    # entries_result[rr.name] = (None, None, None)      # TODO: tenerne traccia in qualche modo
    print("END IP-AS RESOLVER")

    print("\n\nSTART LANDING PAGE RESOLVER")
    landing_page_results = dict()
    for domain_name in domain_name_list:
        print(f"\nTrying to connect to domain '{domain_name}' via https:")
        try:
            landing_url, redirection_path, hsts = requests_utils.resolve_landing_page(domain_name)
            print(f"Landing url: {landing_url}")
            print(f"HTTPS Strict Transport Security: {hsts}")
            print(f"Redirection path:")
            for index, url in enumerate(redirection_path):
                print(f"[{index + 1}/{len(redirection_path)}]: {url}")
            landing_page_results[domain_name] = (landing_url, redirection_path, hsts)
        except Exception as exc:
            print(f"!!! {str(exc)} !!!")
    print("Insertion into database... ", end='')
    helper_landing_page.multiple_inserts(landing_page_results)
    print("DONE.")
    print("END LANDING PAGE RESOLVER")

    print("\n\nSTART CONTENT DEPENDENCIES RESOLVER")
    headless_browser = FirefoxHeadlessWebDriver()
    content_resolver = None
    additional_domain_name_to_be_elaborated = list()
    content_dependencies_result = dict()
    try:
        content_resolver = ContentDependenciesResolver(headless_browser)
    except selenium.common.exceptions.WebDriverException as exc1:
        print(f"!!! {str(exc1)} !!!")
    except GeckoDriverExecutableNotFoundError as exc2:
        print(f"!!! {exc2.message} !!!")
    for domain_name in landing_page_results.keys():
        print(f"Searching content dependencies for: {landing_page_results[domain_name][0]}")
        try:
            content_dependencies = content_resolver.search_script_application_dependencies(landing_page_results[domain_name][0])
            for index, dep in enumerate(content_dependencies):
                print(f"--> [{index+1}]: {str(dep)}")
            content_dependencies_result[landing_page_results[domain_name][0]] = content_dependencies
        except selenium.common.exceptions.WebDriverException as exc:
            print(f"!!! {str(exc)} !!!")
    print("Insertion into database... ", end='')
    helper_content_dependency.multiple_inserts(content_dependencies_result)
    print("DONE.")
    print("END CONTENT DEPENDENCIES RESOLVER")

    print("\n\nSTART ROV PAGE SCRAPING")
    rov_scraping_result_by_as = dict()      # better to be a dict[as_number: dict[nameserver: [info_list]]] ?
    for nameserver in entries_result.keys():
        ip_string = entries_result[nameserver][0]        # str
        entry_ip_as_db = entries_result[nameserver][1]       # EntryIpAsDatabase
        belonging_network_ip_as_db = entries_result[nameserver][2]   # ipaddress.IPv4Network
        try:        # TODO: ci possono essere doppioni... Controllare solo dal nameserver?
            rov_scraping_result_by_as[entry_ip_as_db.as_number].append([nameserver, ip_string, entry_ip_as_db, belonging_network_ip_as_db])
        except KeyError:
            _list = [nameserver, ip_string, entry_ip_as_db, belonging_network_ip_as_db]
            rov_scraping_result_by_as[entry_ip_as_db.as_number] = [_list]
    rov_page_scraper = ROVPageScraper(headless_browser)
    for as_number in rov_scraping_result_by_as.keys():
        print(f"Loading page for AS{as_number}")
        try:
            rov_page_scraper.load_as_page(as_number)
        except selenium.common.exceptions.WebDriverException as exc:
            print(f"!!! {str(exc)} !!!")
            continue
        for list_of_nameserver in rov_scraping_result_by_as[as_number]:
            nameserver = list_of_nameserver[0]
            ip_string = list_of_nameserver[1]
            entry_ip_as_db = list_of_nameserver[2]
            belonging_network_ip_as_db = list_of_nameserver[3]
            try:
                row = rov_page_scraper.get_network_if_present(ipaddress.ip_address(ip_string))
                list_of_nameserver.insert(4, row) # .append(row)
                print(f"--> for '{nameserver}' ({ip_string}), found row: {str(row)}")
            except selenium.common.exceptions.NoSuchElementException as exc:
                print(f"!!! {str(exc)} !!!")
                list_of_nameserver.append(None)
            except (ValueError, NotROVStateTypeError) as exc:
                print(f"!!! {str(exc)} !!!")
                list_of_nameserver.append(None)
            except NetworkNotFoundError as exc:
                print(f"!!! {str(exc)} !!!")
                list_of_nameserver.append(None)

    print("Insertion into database... ", end='')
    for as_number in rov_scraping_result_by_as.keys():
        for list_of_nameserver in rov_scraping_result_by_as[as_number]:
            #
            nameserver = list_of_nameserver[0]
            ip_string = list_of_nameserver[1]
            entry_ip_as_db = list_of_nameserver[2]
            belonging_network_ip_as_db = list_of_nameserver[3]
            entry_rov_page = list_of_nameserver[4]
            #
            ns = helper_nameserver.insert_or_get(nameserver, ip_string)
            eia = helper_entry_ip_as_database.insert_or_get(entry_ip_as_db)
            if entry_rov_page is None:
                helper_matches.insert_or_get_only_entry_ip_as_db(ns, eia)
            else:
                erp = helper_entry_rov_page.insert(entry_rov_page)
                helper_matches.insert_or_get(ns, eia, erp)
                nrps = helper_ip_network.insert_or_get(entry_rov_page.prefix)
                helper_prefix.insert(erp, nrps)
            niad = helper_ip_network.insert_or_get(belonging_network_ip_as_db)
            helper_belonging_network.insert_or_get(entry_ip_as_db.as_number, niad)
    print("DONE.")
    print("END ROV PAGE SCRAPING")
    headless_browser.close()


print("********** START APPLICATION **********")
try:
    application_runner()
except Exception as e:
    take_snapshot(e)
    print(f"!!! Unexpected exception occurred. SNAPSHOT taken. !!!")
    print(f"!!! {str(e)} !!!")
print("********** APPLICATION END **********")
