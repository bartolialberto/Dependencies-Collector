from typing import List, Dict, Union
from peewee import chunked
from persistence.BaseModel import PrefixesTableAssociation, ROVEntity, AutonomousSystemEntity, \
    IpRangeROVEntity, BATCH_SIZE_MAX


def insert(irre: IpRangeROVEntity or None, re: ROVEntity or None, ase: AutonomousSystemEntity) -> PrefixesTableAssociation:
    pta, created = PrefixesTableAssociation.get_or_create(ip_range_rov=irre, rov=re, autonomous_system=ase)
    return pta


# insert + update = upsert
def bulk_upserts(data_source: List[Dict[str, Union[IpRangeROVEntity, ROVEntity, AutonomousSystemEntity, None]]]) -> None:
    """
    Must be invoked inside a peewee transaction. Transaction needs the database object (db).
    Example:
        with db.atomic() as transaction:
            bulk_upserts(...)

    :param data_source: Fields name and values of multiple PrefixesTableAssociation objects in the form of a
    dictionary.
    :type data_source: List[Dict[str, Union[IpRangeROVEntity, ROVEntity, AutonomousSystemEntity, None]]]
    """
    num_of_fields = 3
    batch_size = int(BATCH_SIZE_MAX / (num_of_fields + 1))
    for batch in chunked(data_source, batch_size):
        PrefixesTableAssociation.insert_many(batch).on_conflict_replace().execute()
