import dns.resolver
from pathlib import Path
from entities.IpDatabase import IpDatabase
from entities.TypesRR import TypesRR
from utils import network_utils
from utils import resolver_utils
from utils import domain_name_utils


print("********** START **********")
print(f"Local IP: {network_utils.get_local_ip()}")
print(f"Current working directory: {Path.cwd()}")
path_ip2asn = 'C:\\Users\\fabbi\\PycharmProjects\\ThesisWork\\file_cache\\ip2asn-v4.tsv' #C:/Users/leona/Desktop/TesiMagistrale/IPv4ToASN/ip2asn-v4.tsv
path_firefox = '"C:\\Program Files\\Mozilla Firefox\\firefox.exe"' #C:/Program Files/Mozilla Firefox/firefox.exe
path_geckodriver = 'C:\\geckodriver-v0.30.0-win64' #C:/Users/Alberto/Downloads/geckodriver


# d = "google.com"
# d = "www.google.com"
# d = "www.google.it"
# d = "www.darklyrics.com"
# d = "www.easupersian.com"
# d = "www.networkfabbio.ns0.it"
# d = "www.tubebooks.org"
d = "www.dyndns.it"
# d = "www.units.it"
# d = "dia.units.it"
# d = "www.inginf.units.it"

domain_name_utils.grammatically_correct(d)

r = dns.resolver.Resolver()
r.nameservers = ["1.1.1.1"]

(response, aliases) = resolver_utils.search_resource_records(r, d, TypesRR.A)
ip = response.get_first_value()
zone_list, cache, error_logs = resolver_utils.search_domain_dns_dependencies(r, d)
cache.write_to_csv_file()
error_logs.write_to_csv_file()

try:
    ip_database = IpDatabase()
    entry = ip_database.resolve_range(ip)
    print(entry)
except FileNotFoundError as e:
    print(str(e))

print("********** END **********")
