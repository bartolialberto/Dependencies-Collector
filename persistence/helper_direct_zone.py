from typing import Set
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence.BaseModel import DirectZoneAssociation, DomainNameEntity, ZoneEntity


def insert(dne: DomainNameEntity, ze: ZoneEntity or None) -> DirectZoneAssociation:
    dza, created = DirectZoneAssociation.get_or_create(domain_name=dne, zone=ze)
    return dza


def get_from_zone_dataset(zes: Set[ZoneEntity]) -> Set[DirectZoneAssociation]:
    query = DirectZoneAssociation.select()\
        .where(DirectZoneAssociation.zone.in_(zes))
    result = set()
    for row in query:
        result.add(row)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result
