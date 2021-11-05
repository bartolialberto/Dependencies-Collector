import dns.resolver
from pathlib import Path
from utils import file_utils
from utils import network_utils
from utils import resolver_utils
from Zones import RRecord
import exceptions


print(f"local_ip = {network_utils.get_local_ip()}")
# print(f"external_ip = {network_utils.get_public_ip_from_ident_me()}")
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
# d = "www.dyndns.it"
d = "www.units.it"
# d = "dia.units.it"
# d = "www.inginf.units.it"

r = dns.resolver.Resolver()
r.nameservers = ["1.1.1.1"]
print(f"START for domain_name = {d}")
result = resolver_utils.find_dns_info(r, d)

print("THE END")
