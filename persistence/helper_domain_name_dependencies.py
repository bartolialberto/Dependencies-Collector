from typing import List, Dict, Union
from persistence.BaseModel import DomainNameEntity, ZoneEntity, DomainNameDependenciesAssociation


def insert(dne: DomainNameEntity, ze: ZoneEntity) -> DomainNameDependenciesAssociation:
    nda, created = DomainNameDependenciesAssociation.get_or_create(domain_name=dne, zone=ze)
    return nda


def bulk_upserts(data_source: List[Dict[str, Union[DomainNameEntity, ZoneEntity]]]) -> None:
    DomainNameDependenciesAssociation.insert_many(data_source).on_conflict_replace().execute()

