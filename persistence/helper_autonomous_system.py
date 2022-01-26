from typing import Set
from peewee import DoesNotExist
from persistence.BaseModel import AutonomousSystemEntity, IpRangeTSVEntity, NetworkNumbersAssociation, DomainNameEntity, \
    AccessAssociation, IpAddressDependsAssociation


def insert(as_number: int, description: str) -> AutonomousSystemEntity:
    ase, created = AutonomousSystemEntity.get_or_create(number=as_number, description=description)
    return ase


def get(as_number: int) -> AutonomousSystemEntity:
    try:
        return AutonomousSystemEntity.get_by_id(as_number)
    except DoesNotExist:
        raise


def get_of_entity_ip_range_tsv(irte: IpRangeTSVEntity) -> AutonomousSystemEntity:
    query = NetworkNumbersAssociation.select()\
        .where(NetworkNumbersAssociation.ip_range_tsv == irte)\
        .limit(1)
    for row in query:
        return row.autonomous_system
    raise DoesNotExist


def get_of_entity_domain_name(dne: DomainNameEntity) -> Set[AutonomousSystemEntity]:
    query = NetworkNumbersAssociation.select()\
        .join(IpAddressDependsAssociation, on=(IpAddressDependsAssociation.ip_range_tsv == NetworkNumbersAssociation.ip_range_tsv))\
        .join(AccessAssociation, on=(AccessAssociation.ip_address == IpAddressDependsAssociation.ip_address))\
        .where(AccessAssociation.domain_name == dne)
    result = set()
    for row in query:
        result.add(row.autonomous_system)
    return result
