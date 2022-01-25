from typing import Set, Tuple
from persistence.BaseModel import PrefixesTableAssociation, ROVEntity, AutonomousSystemEntity, \
    IpRangeROVEntity


def insert(irre: IpRangeROVEntity or None, re: ROVEntity or None, ase: AutonomousSystemEntity) -> PrefixesTableAssociation:
    pta, created = PrefixesTableAssociation.get_or_create(ip_range_rov=irre, rov=re, autonomous_system=ase)
    return pta


def get_all_from(ase: AutonomousSystemEntity) -> Set[Tuple[IpRangeROVEntity, ROVEntity]]:
    query = PrefixesTableAssociation.select()\
        .where(PrefixesTableAssociation.autonomous_system == ase)
    result = set()
    for row in query:
        result.add((row.ip_network, row.rov))
    return result
