import ipaddress
from persistence import helper_has
from persistence.BaseModel import IpRangeEntity, EntryIpAsDatabaseEntity, HasAssociation


def insert(start_ip: ipaddress.IPv4Address, end_ip: ipaddress.IPv4Address) -> IpRangeEntity:
    re, created = IpRangeEntity.get_or_create(start=start_ip.compressed, end=end_ip.compressed)
    return re


def insert_with_relation_too(entry: EntryIpAsDatabaseEntity, start_ip: ipaddress.IPv4Address, end_ip: ipaddress.IPv4Address) -> (IpRangeEntity, HasAssociation):
    re = insert(start_ip, end_ip)
    ha = helper_has.insert(entry, re)
    return re, ha
