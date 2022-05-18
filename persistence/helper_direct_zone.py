from typing import Set, List, Dict, Union
from peewee import chunked
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence.BaseModel import DirectZoneAssociation, DomainNameEntity, ZoneEntity, BATCH_SIZE_MAX, \
    NORMALIZATION_CONSTANT


def insert(dne: DomainNameEntity, ze: ZoneEntity or None) -> DirectZoneAssociation:
    dza, created = DirectZoneAssociation.get_or_create(domain_name=dne, zone=ze)
    return dza


# insert + update = upsert
def bulk_upserts(data_source: List[Dict[str, Union[DomainNameEntity, ZoneEntity, None]]]) -> None:
    """
    Must be invoked inside a peewee transaction. Transaction needs the database object (db).
    Example:
        with db.atomic() as transaction:
            bulk_upserts(...)

    :param data_source: Fields name and values of multiple DirectZoneAssociation objects in the form of a dictionary.
    :type data_source: List[Dict[str, Union[DomainNameEntity, ZoneEntity, None]]]
    """
    num_of_fields = 2
    batch_size = int(BATCH_SIZE_MAX / (num_of_fields + NORMALIZATION_CONSTANT))
    for batch in chunked(data_source, batch_size):
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
