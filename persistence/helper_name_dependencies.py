from typing import Set
from peewee import DoesNotExist
from persistence import helper_domain_name
from persistence.BaseModel import DomainNameEntity, ZoneEntity, NameDependenciesAssociation


def insert(dne: DomainNameEntity, ze: ZoneEntity) -> NameDependenciesAssociation:
    nda, created = NameDependenciesAssociation.get_or_create(domain_name=dne, zone=ze)
    return nda


def get_all_of(domain_name: str) -> Set[NameDependenciesAssociation]:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    result = set()
    query = NameDependenciesAssociation.select().where(NameDependenciesAssociation.domain_name == dne)
    for row in query:
        result.add(row)
    return result
