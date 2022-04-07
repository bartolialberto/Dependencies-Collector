from typing import Set
from peewee import DoesNotExist

from entities.DomainName import DomainName
from exceptions.NoAliasFoundError import NoAliasFoundError
from persistence import helper_domain_name
from persistence.BaseModel import DomainNameEntity, AliasAssociation


def insert(dne: DomainNameEntity, adne: DomainNameEntity) -> AliasAssociation:
    aa, created = AliasAssociation.get_or_create(name=dne, alias=adne)
    return aa


def get_alias_from_entity(dne: DomainNameEntity) -> DomainNameEntity:
    try:
        aa = AliasAssociation.get(AliasAssociation.name == dne)
    except DoesNotExist:
        raise
    return aa.alias


def get_alias(domain_name: DomainName) -> DomainNameEntity:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    return get_alias_from_entity(dne)


def get_all_aliases_from_entity(dne: DomainNameEntity) -> Set[DomainNameEntity]:
    """ Query probably useful only for tests. """
    result = set()
    query = AliasAssociation.select() \
        .join(DomainNameEntity, on=(AliasAssociation.name == dne))
    for row in query:
        result.add(row.alias)
    if len(result) == 0:
        raise NoAliasFoundError(dne.string)
    else:
        return result
