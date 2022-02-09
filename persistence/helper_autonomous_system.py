from typing import Set
from peewee import DoesNotExist

from persistence import helper_domain_name
from persistence.BaseModel import AutonomousSystemEntity, IpRangeTSVEntity, NetworkNumbersAssociation, DomainNameEntity, \
    AccessAssociation, IpAddressDependsAssociation, IpAddressEntity, IpNetworkEntity


def insert(as_number: int, description: str) -> AutonomousSystemEntity:
    ase, created = AutonomousSystemEntity.get_or_create(number=as_number, description=description)
    return ase


def get(as_number: int) -> AutonomousSystemEntity:
    try:
        return AutonomousSystemEntity.get_by_id(as_number)
    except DoesNotExist:
        raise


def get_of_entity_ip_address(iae: IpAddressEntity) -> AutonomousSystemEntity:
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
    query = NetworkNumbersAssociation.select()\
        .where(NetworkNumbersAssociation.ip_range_tsv == irte)\
        .limit(1)
    for row in query:
        return row.autonomous_system
    raise DoesNotExist


def get_of_entity_domain_name(dne: DomainNameEntity) -> Set[AutonomousSystemEntity]:
    iaes, dnes = helper_domain_name.resolve_access_path(dne, get_only_first_address=False)
    result = set()
    for iae in iaes:
        ase = get_of_entity_ip_address(iae)
        result.add(ase)
    return result
