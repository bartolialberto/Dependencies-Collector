from peewee import DoesNotExist
from persistence.BaseModel import AutonomousSystemEntity, IpRangeTSVEntity, NetworkNumbersAssociation


def insert(as_number: int) -> AutonomousSystemEntity:
    ase, created = AutonomousSystemEntity.get_or_create(number=as_number)
    return ase


def get_of_entity_ip_range_tsv(irte: IpRangeTSVEntity) -> AutonomousSystemEntity:
    query = NetworkNumbersAssociation.select()\
        .join_from(NetworkNumbersAssociation, AutonomousSystemEntity)\
        .where(NetworkNumbersAssociation.ip_range_tsv == irte)\
        .limit(1)
    for row in query:
        return row.autonomous_system
    raise DoesNotExist
