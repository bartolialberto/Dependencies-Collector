import ipaddress
from entities.IpAsDatabase import IpAsDatabase
from entities.LocalResolverCache import LocalResolverCache
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from utils import csv_utils


db = IpAsDatabase()
ip = ipaddress.ip_address("199.9.14.201")
try:
    entry = db.resolve_range(ip)
except AutonomousSystemNotFoundError as e:
    print(f"!!!  {str(e)} !!!")
    exit(1)
try:
    belonging_network, networks = entry.get_network_of_ip(ip)
    for i, network in enumerate(networks):
        print(f"network[{str(i+1)}]: {network.compressed}")
    print(f"belonging_network: {belonging_network.compressed}")
except ValueError as f:
    print(f"!!!  {str(f)} !!!")
    exit(1)

print("THE END")
