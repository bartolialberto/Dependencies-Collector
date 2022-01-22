from typing import Set
from peewee import DoesNotExist
from persistence import helper_domain_name
from persistence.BaseModel import DomainNameEntity, ZoneEntity, DomainNameDependenciesAssociation


def insert(dne: DomainNameEntity, ze: ZoneEntity) -> DomainNameDependenciesAssociation:
    nda, created = DomainNameDependenciesAssociation.get_or_create(domain_name=dne, zone=ze)
    return nda


def get_all_of(domain_name: str) -> Set[ZoneEntity]:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    result = set()
    query = DomainNameDependenciesAssociation.select().where(DomainNameDependenciesAssociation.domain_name == dne)
    for row in query:
        result.add(row.zone)
    return result
