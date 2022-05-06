from typing import List, Dict, Union
from peewee import chunked
from persistence.BaseModel import DomainNameEntity, ZoneEntity, DomainNameDependenciesAssociation, BATCH_SIZE_MAX


def insert(dne: DomainNameEntity, ze: ZoneEntity) -> DomainNameDependenciesAssociation:
    nda, created = DomainNameDependenciesAssociation.get_or_create(domain_name=dne, zone=ze)
    return nda


def bulk_upserts(data_source: List[Dict[str, Union[DomainNameEntity, ZoneEntity]]]) -> None:
    """
    Must be invoked inside a peewee transaction. Transaction needs the database object (db).
    Example:
        with db.atomic() as transaction:
            bulk_upserts(...)

    :param data_source: Fields name and values of multiple DomainNameDependenciesAssociation objects in the form of a
    dictionary.
    :type data_source: List[Dict[str, Union[DomainNameEntity, ZoneEntity]]]
    """
    num_of_fields = 2
    batch_size = int(BATCH_SIZE_MAX / (num_of_fields + 1))
    for batch in chunked(data_source, batch_size):
        DomainNameDependenciesAssociation.insert_many(batch).on_conflict_replace().execute()
