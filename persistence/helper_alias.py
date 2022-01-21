from typing import Set
from peewee import DoesNotExist
from exceptions.NoAliasFoundError import NoAliasFoundError
from persistence import helper_domain_name
from persistence.BaseModel import DomainNameEntity, AliasAssociation


def insert(dne: DomainNameEntity, adne: DomainNameEntity) -> AliasAssociation:
    aa, created = AliasAssociation.get_or_create(name=dne, alias=adne)
    return aa


def get_all_aliases_from_entity(dne: DomainNameEntity) -> Set[DomainNameEntity]:
    result = set()
    query = AliasAssociation.select() \
        .join(DomainNameEntity, on=(AliasAssociation.name == dne))
    for row in query:
        result.add(row.alias)
    if len(result) == 0:
        raise NoAliasFoundError(dne.name)
    else:
        return result


def get_all_aliases_from_name(domain_name: str) -> Set[DomainNameEntity]:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    try:
        return get_all_aliases_from_entity(dne)
    except NoAliasFoundError:
        raise
