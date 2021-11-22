import ipaddress
import dns.resolver
from dns.resolver import NoAnswer
from dns.resolver import NXDOMAIN
import Zones
from DomainDependence import DomainDependence
from NetNumberResolver import NetNumberResolver
from Resolver import Resolver
from pathlib import Path
from Zones import RRecord


path_ip2asn = 'C:\\Users\\fabbi\\PycharmProjects\\ThesisWork\\file_cache\\ip2asn-v4.tsv' #C:/Users/leona/Desktop/TesiMagistrale/IPv4ToASN/ip2asn-v4.tsv
path_firefox = '"C:\\Program Files\\Mozilla Firefox\\firefox.exe"' #C:/Program Files/Mozilla Firefox/firefox.exe
path_geckodriver = 'C:\\geckodriver-v0.30.0-win64' #C:/Users/Alberto/Downloads/geckodriver

listRange = DomainDependence.rangeVerificated("AS21342", ["96.7.49.0/22", "95.100.168.0/24"], dPath=path_geckodriver, fPath=path_firefox)
print("Network  |   VLD")
for l in listRange:
    print(l[0], "   |   ", l[1])

print("THE END")