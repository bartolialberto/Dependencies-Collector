from typing import List, Dict, Union
from peewee import chunked
from persistence.BaseModel import DomainNameEntity, ZoneEntity, DomainNameDependenciesAssociation


def insert(dne: DomainNameEntity, ze: ZoneEntity) -> DomainNameDependenciesAssociation:
    nda, created = DomainNameDependenciesAssociation.get_or_create(domain_name=dne, zone=ze)
    return nda


def bulk_upserts(data_source: List[Dict[str, Union[DomainNameEntity, ZoneEntity]]]) -> None:
    for batch in chunked(data_source, 400):
        DomainNameDependenciesAssociation.insert_many(batch).on_conflict_replace().execute()

