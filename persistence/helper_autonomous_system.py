import ipaddress
from typing import Set, Union
from peewee import DoesNotExist
from entities.resolvers.IpAsDatabase import EntryIpAsDatabase
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_domain_name, helper_ip_address
from persistence.BaseModel import AutonomousSystemEntity, IpRangeTSVEntity, NetworkNumbersAssociation, DomainNameEntity, \
    AccessAssociation, IpAddressDependsAssociation, IpAddressEntity, IpNetworkEntity


def insert(entry: EntryIpAsDatabase) -> AutonomousSystemEntity:
    ase, created = AutonomousSystemEntity.get_or_create(number=entry.as_number, description=entry.as_description, country_code=entry.country_code)
    return ase


def get(as_number: int) -> AutonomousSystemEntity:
    try:
        return AutonomousSystemEntity.get_by_id(as_number)
    except DoesNotExist:
        raise


def get_of_ip_address(iae: IpAddressEntity) -> AutonomousSystemEntity:
    query = NetworkNumbersAssociation.select()\
        .join(IpAddressDependsAssociation, on=(IpAddressDependsAssociation.ip_range_tsv == NetworkNumbersAssociation.ip_range_tsv))\
        .where(IpAddressDependsAssociation.ip_address == iae)\
        .limit(1)
    for row in query:
        return row.autonomous_system
    raise DoesNotExist


def get_of_entity_ip_network(ine: IpNetworkEntity) -> AutonomousSystemEntity:
    query = NetworkNumbersAssociation.select()\
        .join(IpAddressDependsAssociation, on=(IpAddressDependsAssociation.ip_range_tsv == NetworkNumbersAssociation.ip_range_tsv))\
        .where(IpAddressDependsAssociation.ip_network == ine)\
        .limit(1)
    for row in query:
        return row.autonomous_system
    raise DoesNotExist


def get_of_entity_ip_range_tsv(irte: IpRangeTSVEntity) -> AutonomousSystemEntity:
    """
    query = NetworkNumbersAssociation.select()\
        .where(NetworkNumbersAssociation.ip_range_tsv == irte)\
        .limit(1)
    for row in query:
        return row.autonomous_system
    raise DoesNotExist
    """

    try:
        nna = NetworkNumbersAssociation.get(NetworkNumbersAssociation.ip_range_tsv == irte)
        return nna.autonomous_system
    except DoesNotExist:
        raise


def get_of_entity_domain_name(dne: DomainNameEntity) -> Set[AutonomousSystemEntity]:
    iaes, dnes = helper_domain_name.resolve_a_path(dne, get_only_first_address=False)
    result = set()
    for iae in iaes:
        ase = get_of_ip_address(iae)
        result.add(ase)
    return result


def get_all_ip_addresses_of(ase: AutonomousSystemEntity) -> Set[IpAddressEntity]:
    query = IpAddressDependsAssociation.select()\
        .join(NetworkNumbersAssociation, on=(NetworkNumbersAssociation.ip_range_tsv == IpAddressDependsAssociation.ip_range_tsv))\
        .where(NetworkNumbersAssociation.autonomous_system == ase)
    result = set()
    for row in query:
        result.add(row.ip_address)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result


def get_everyone() -> Set[AutonomousSystemEntity]:
    result = set()
    query = AutonomousSystemEntity.select()
    for row in query:
        result.add(row)
    return result
