import dns.resolver
from pathlib import Path
from entities.TypesRR import TypesRR
from utils import file_utils
from utils import network_utils
from utils import resolver_utils
from exceptions.UnknownReasonError import UnknownReasonError
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.NoAnswerError import NoAnswerError


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
d = "dyndns.it"
# d = "www.units.it"
# d = "dia.units.it"
# d = "www.inginf.units.it"

r = dns.resolver.Resolver()
r.nameservers = ["1.1.1.1"]
print(f"********** START for domain_name = {d} **********")
try:
    response, rr_aliases = resolver_utils.search_resource_records(r, d, TypesRR.NS)
    print("RESPONSE:")
    for i, val in enumerate(response.values):
        print(f"response.values[{i}] = {val}")
    print("ALIASES:")
    for j, rr_alias in enumerate(rr_aliases):
        print(f"rr_aliases[{j}] = {rr_alias.values[0]}")
        if len(rr_alias.values) > 1:
            print(f"rr_alias has more than 1 value...")
            for l, alias_val in enumerate(rr_alias.values):
                print(f"----> [{l+1}] = {alias_val}")
except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
    print(f"(!) {e.message}")

print(" ********** THE END  **********")
