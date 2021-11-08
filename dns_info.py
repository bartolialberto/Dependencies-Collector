import dns.resolver
from pathlib import Path
from utils import network_utils, domain_name_utils, resolver_utils


print("********** START **********\n")
print(f"Local IP: {network_utils.get_local_ip()}")
print(f"Current working directory: {Path.cwd()}")
# print(f"external_ip = {network_utils.get_public_ip_from_ident_me()}")
path_ip2asn = 'C:\\Users\\fabbi\\PycharmProjects\\ThesisWork\\file_cache\\ip2asn-v4.tsv' #C:/Users/leona/Desktop/TesiMagistrale/IPv4ToASN/ip2asn-v4.tsv
path_firefox = '"C:\\Program Files\\Mozilla Firefox\\firefox.exe"' #C:/Program Files/Mozilla Firefox/firefox.exe
path_geckodriver = 'C:\\geckodriver-v0.30.0-win64' #C:/Users/Alberto/Downloads/geckodriver


d1 = "google.com"
d2 = "www.google.com"
# d = "www.google.it"
# d = "www.darklyrics.com"
# d = "www.easupersian.com"
# d = "www.networkfabbio.ns0.it"
# d = "www.tubebooks.org"
# d = "www.dyndns.it"
# d = "www.units.it"
# d = "dia.units.it"
# d = "www.inginf.units.it"

domain_name_utils.grammatically_correct(d1)
domain_name_utils.grammatically_correct(d2)

d = [d1, d2]

resolver = dns.resolver.Resolver()
resolver.nameservers = ["1.1.1.1"]
results, cache, error_logs = resolver_utils.search_domains_dns_dependencies(resolver, d)
cache.write_to_csv_file()
error_logs.write_to_txt_file()
print("********** END **********")

