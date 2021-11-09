import os
import sys
import dns.resolver
from pathlib import Path
import requests
import selenium
from entities.FirefoxContentDependenciesResolver import FirefoxContentDependenciesResolver
from entities.IpDatabase import IpDatabase
from entities.LandingSiteHttpResolver import LandingSiteHttpResolver
from entities.LandingSiteHttpsResolver import LandingSiteHttpsResolver
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.GeckoDriverExecutableNotFoundError import GeckoDriverExecutableNotFoundError
from utils import network_utils, list_utils
from utils import resolver_utils
from utils import domain_name_utils


print("********** START APPLICATION **********")
print(f"Local IP: {network_utils.get_local_ip()}")
print(f"Current working directory: {Path.cwd()}")

firefox_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"

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

domain_name_list = list()
if len(sys.argv) == 1:
    print(f"> No command line arguments found. Do you want to write it down now?")
    answer = input(f"> Press 'y' or 'n': ")
    if answer == 'y' or answer == 'Y':
        finished = False
        while not finished:
            print(f"> Current domain name list: {str(domain_name_list)}")
            print(f"> Write 'ok' to finish")
            print(f"> Write 'del' to delete last element of the list.")
            print(f"> Write a domain name and then enter to add.")
            answer = input(f"> ")
            if answer == 'ok' or answer == 'OK':
                finished = True
            elif answer == 'del' or answer == 'DEL':
                try:
                    domain_name_list.pop()
                except IndexError:
                    print(f"!!! you can't delete from an empty list !!!")
            else:
                if domain_name_utils.is_grammatically_correct(answer):
                    domain_name_list.append(answer)
                else:
                    print(f"!!! {answer} is not a well-formatted domain name. !!!")
        if len(domain_name_list) == 0:
            exit(0)
    else:
        exit(0)
else:
    print('> Argument List:', str(sys.argv))
    for arg in sys.argv:
        if domain_name_utils.is_grammatically_correct(arg):
            pass
        else:
            print(f"!!! {arg} is not a well-formatted domain name. !!!")
list_utils.remove_duplicates(domain_name_list)

# DNS DEPENDENCIES RESOLVER
print("START DNS DEPENDENCIES RESOLVER")
dns_resolver = dns.resolver.Resolver()
dns_resolver.nameservers = ["1.1.1.1"]
results, cache, error_logs = resolver_utils.search_domains_dns_dependencies(dns_resolver, domain_name_list)
print(f"> Do you want to export cache and error logs to file in the {os.sep}output folder?")
answer = input(f"> Press 'y' or 'n': ")
if answer == 'y' or answer == 'Y':
    cache.write_to_csv_file()
    error_logs.write_to_csv_file()
else:
    pass
print("END DNS DEPENDENCIES RESOLVER\n")

print("START IP-AS RESOLVER")
try:
    ip_database = IpDatabase()
except FileNotFoundError as e:
    print(f"!!! {str(e)} !!!")
    exit(1)
print(f"> Do you want a print for every nameserver IP-AS resolution for each zone? (Can be a lot VERBOSE)")
answer = input(f"> Press 'y' or 'n': ")
verbose = False
if answer == 'y' or answer == 'Y':
    verbose = True
entries_found = list()
not_found_counter = 0
for index_domain, domain in enumerate(results.keys()):
    print(f"Handling domain[{index_domain}] '{domain}'")
    for index_zone, zone in enumerate(results[domain][0]):
        if verbose:
            print(f"--> Handling zone[{index_zone}] '{zone.name}'")
        for index_rr, rr in enumerate(zone.zone_nameservers):
            try:
                entry = ip_database.resolve_range(rr.get_first_value())
                entries_found.append(entry)
                if verbose:
                    print(f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) found AS record: [{entry}]")
            except AutonomousSystemNotFoundError:
                not_found_counter += 1
                if verbose:
                    print(f"----> for nameserver[{index_rr}] '{rr.name}' ({rr.get_first_value()}) no AS record found.")
print(f"Found {len(entries_found)}/{len(entries_found)+not_found_counter} entries.")
print("END IP-AS RESOLVER\n")

print("START CONTENT DEPENDENCIES RESOLVER")
print("Make sure no instance of Firefox is already running in your computer.")
try:
    content_resolver = FirefoxContentDependenciesResolver()
    content_dependencies, domain_list = content_resolver.search_script_application_dependencies("DOMAIN_NAME")
    content_resolver.close()
    print(f"javascript/application dependencies found: {len(content_dependencies)} on {len(domain_list)} domains.")
except selenium.common.exceptions.WebDriverException as e:
    print(f"!!! {str(e)} !!!")
except GeckoDriverExecutableNotFoundError as e2:
    print(f"!!! {e2.message} !!!")
print("END CONTENT DEPENDENCIES RESOLVER\n")

print("START LANDING PAGE RESOLVER")
domain = "www.prova.lol"
print(f"Trying to connect to domain '{domain}' via https:")
try:
    landing_site_resolver = LandingSiteHttpsResolver(domain)
    print(f"Landing url: {landing_site_resolver.landing_url}\nLanding domain: {landing_site_resolver.landing_domain}")
    print(f"Redirection path:")
    for index, url in enumerate(landing_site_resolver.redirection_path):
        print(f"[{index + 1}/{len(landing_site_resolver.redirection_path)}]: {url}")
    print(f"Is there a domain redirection? {landing_site_resolver.domain_redirection}")
except requests.exceptions.ConnectionError as e:
    try:
        print(f"Seems that https is not supported.")
        print(f"Trying to connect to domain '{domain}' via http:")
        landing_site_resolver = LandingSiteHttpResolver(domain)
        print(f"Landing url: {landing_site_resolver.landing_url}\nLanding domain: {landing_site_resolver.landing_domain}")
        print(f"Redirection path:")
        for index, url in enumerate(landing_site_resolver.redirection_path):
            print(f"[{index + 1}/{len(landing_site_resolver.redirection_path)}]: {url}")
        print(f"Is there a domain redirection? {landing_site_resolver.domain_redirection}")
    except Exception as e:
        print(f"!!! {str(e)} !!!")
except Exception as e:
    print(f"!!! {str(e)} !!!")
print("END LANDING PAGE RESOLVER\n")

print("********** APPLICATION END **********")
