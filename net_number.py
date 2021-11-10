import ipaddress
from entities.IpAsDatabase import IpAsDatabase
from pathlib import Path
from utils import network_utils


print("********** START **********")
print(f"Local IP: {network_utils.get_local_ip()}")
print(f"Current working directory: '{Path.cwd()}'")
ip_database_path = "testing/input/ip2asn-v4.tsv"
ip = ipaddress.ip_address('82.56.79.188')

try:
    ip_database = IpAsDatabase()
    entry = ip_database.resolve_range(ip)
    print(entry)
except FileNotFoundError as e:
    print(str(e))

print("********** END **********")
