from typing import List, Dict, Union
from peewee import chunked
from persistence.BaseModel import NetworkNumbersAssociation, IpRangeTSVEntity, AutonomousSystemEntity, BATCH_SIZE_MAX, \
    NORMALIZATION_CONSTANT


def insert(irte: IpRangeTSVEntity, ase: AutonomousSystemEntity) -> NetworkNumbersAssociation:
    nna, created = NetworkNumbersAssociation.get_or_create(ip_range_tsv=irte, autonomous_system=ase)
    return nna


# insert + update = upsert
def bulk_upserts(data_source: List[Dict[str, Union[IpRangeTSVEntity, AutonomousSystemEntity]]]) -> None:
    """
    Must be invoked inside a peewee transaction. Transaction needs the database object (db).
    Example:
        with db.atomic() as transaction:
            bulk_upserts(...)

    :param data_source: Fields name and values of multiple NetworkNumbersAssociation objects in the form of a
    dictionary.
    :type data_source: List[Dict[str, Union[IpRangeTSVEntity, AutonomousSystemEntity]]]
    """
    num_of_fields = 2
    batch_size = int(BATCH_SIZE_MAX / (num_of_fields + NORMALIZATION_CONSTANT))
    for batch in chunked(data_source, batch_size):
        NetworkNumbersAssociation.insert_many(batch).on_conflict_replace().execute()
