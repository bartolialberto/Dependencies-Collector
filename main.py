import ipaddress
import sys
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from take_snapshot import take_snapshot
from pathlib import Path
import requests
import selenium
from entities.DnsResolver import DnsResolver
from entities.FirefoxContentDependenciesResolver import FirefoxContentDependenciesResolver
from entities.IpAsDatabase import IpAsDatabase
from entities.LandingSiteHttpResolver import LandingSiteHttpResolver
from entities.LandingSiteHttpsResolver import LandingSiteHttpsResolver
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from exceptions.GeckoDriverExecutableNotFoundError import GeckoDriverExecutableNotFoundError
from exceptions.NoValidDomainNamesFoundError import NoValidDomainNamesFoundError
from utils import network_utils, list_utils, shell_utils, downloads_utils
from utils import domain_name_utils


def application_runner():
    print(f"Local IP: {network_utils.get_local_ip()}")
    print(f"Current working directory: {Path.cwd()}")

    firefox_string_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
    firefox_path = Path(firefox_string_path)
    if firefox_path.exists() and firefox_path.is_file():
        print(f"Firefox executable filepath: {firefox_string_path}")
    else:
        print(f"!!! firefoxpath: {firefox_string_path} is not valid. !!!")
        exit(1)

    # d = "google.com"
    # d = "www.google.com"
    # d = "www.google.it"
    # d = "www.darklyrics.com"
    # d = "www.easupersian.com"
    # d = "www.networkfabbio.ns0.it"
    # d = "www.tubebooks.org"
    # d = "www.dyndns.it"
    # d = "www.units.it"
    # d = "dia.units.it"
    # d = "www.inginf.units.it"

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
    results = dns_resolver.search_multiple_domains_dependencies(domain_name_list)
    # export
    dns_resolver.cache.write_to_csv_in_output_folder()
    dns_resolver.error_logs.write_to_csv_in_output_folder()
    print("END DNS DEPENDENCIES RESOLVER")

    print("\n\nSTART IP-AS RESOLVER")
    print(f"> Do you want to download latest ip-as database from https://iptoasn.com/ ?")
    answer = shell_utils.wait_yes_or_no_response("> ")
    if answer == 'y' or answer == 'Y':
        try:
            downloads_utils.download_latest_tsv_database()
            print("Latest database was downloaded and extracted successfully.")
        except FileWithExtensionNotFoundError as err:
            print(f"!!! {str(err)} !!!")
    else:
        pass
    try:
        ip_as_db = IpAsDatabase()
    except (FileWithExtensionNotFoundError, OSError) as exc:
        print(f"!!! {str(exc)} !!!")
        exit(1)
    entries_found = list()
    not_found_counter = 0
    for index_domain, domain in enumerate(results.keys()):
        print(f"Handling domain[{index_domain}] '{domain}'")
        for index_zone, zone in enumerate(results[domain]):
            print(f"--> Handling zone[{index_zone}] '{zone.name}'")
            for index_rr, rr in enumerate(zone.zone_nameservers):
                try:
                    ip = ipaddress.IPv4Address(rr.get_first_value())
                    entry = ip_as_db.resolve_range(ip)
                    entries_found.append(entry)
                    try:
                        belonging_network, networks = entry.get_network_of_ip(ip)
                        print(
                            f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) found AS record: [{entry}]. Belonging network: {belonging_network.compressed}")
                    except ValueError:
                        print(
                            f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) found AS record: [{entry}]")
                except AutonomousSystemNotFoundError:
                    not_found_counter += 1
                    print(f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) no AS record found.")
    print(f"Found {len(entries_found)}/{len(entries_found)+not_found_counter} entries.")
    print("END IP-AS RESOLVER")

    print("\n\nSTART CONTENT DEPENDENCIES RESOLVER")
    print("Make sure no instance of Firefox is already running in your computer.")
    content_resolver = None
    try:
        content_resolver = FirefoxContentDependenciesResolver()
    except selenium.common.exceptions.WebDriverException as exc1:
        print(f"!!! {str(exc1)} !!!")
    except GeckoDriverExecutableNotFoundError as exc2:
        print(f"!!! {exc2.message} !!!")
    for domain_name in domain_name_list:
        print(f"Resolving content for: {domain_name}..")
        try:
            content_dependencies, domain_list = content_resolver.search_script_application_dependencies(domain_name)
            print(f"javascript/application dependencies found: {len(content_dependencies)} on {len(domain_list)} domains.")
        except selenium.common.exceptions.WebDriverException as exc:
            print(f"!!! {str(exc)} !!!")
    content_resolver.close()
    print("END CONTENT DEPENDENCIES RESOLVER\n")

    print("START LANDING PAGE RESOLVER")
    for domain_name in domain_name_list:
        print(f"Trying to connect to domain '{domain_name}' via https:")
        try:
            landing_site_resolver = LandingSiteHttpsResolver(domain_name)
            print(f"Landing url: {landing_site_resolver.landing_url}\nLanding domain: {landing_site_resolver.landing_domain}")
            print(f"Redirection path:")
            for index, url in enumerate(landing_site_resolver.redirection_path):
                print(f"[{index + 1}/{len(landing_site_resolver.redirection_path)}]: {url}")
            print(f"Is there a domain redirection? {landing_site_resolver.domain_redirection}")
        except requests.exceptions.ConnectionError:
            try:
                print(f"Seems that https is not supported.")
                print(f"Trying to connect to domain '{domain_name}' via http:")
                landing_site_resolver = LandingSiteHttpResolver(domain_name)
                print(f"Landing url: {landing_site_resolver.landing_url}\nLanding domain: {landing_site_resolver.landing_domain}")
                print(f"Redirection path:")
                for index, url in enumerate(landing_site_resolver.redirection_path):
                    print(f"[{index + 1}/{len(landing_site_resolver.redirection_path)}]: {url}")
                print(f"Is there a domain redirection? {landing_site_resolver.domain_redirection}")
            except Exception as exception:
                print(f"!!! {str(exception)} !!!")
        except Exception as exc:
            print(f"!!! {str(exc)} !!!")
    print("END LANDING PAGE RESOLVER")


print("********** START APPLICATION **********")
try:
    application_runner()
except Exception as e:
    take_snapshot(e)
    print(f"!!! Unexpected exception occurred. SNAPSHOT taken. !!!")
    print(f"!!! {str(e)} !!!")
print("********** APPLICATION END **********")
