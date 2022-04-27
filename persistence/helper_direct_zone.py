from typing import Set, List, Dict, Union
from peewee import chunked
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence.BaseModel import DirectZoneAssociation, DomainNameEntity, ZoneEntity


def insert(dne: DomainNameEntity, ze: ZoneEntity or None) -> DirectZoneAssociation:
    dza, created = DirectZoneAssociation.get_or_create(domain_name=dne, zone=ze)
    return dza


def bulk_upserts(data_source: List[Dict[str, Union[DomainNameEntity, ZoneEntity, None]]]) -> None:
    for batch in chunked(data_source, 600):
        DirectZoneAssociation.insert_many(batch).on_conflict_replace().execute()


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
