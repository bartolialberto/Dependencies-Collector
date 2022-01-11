from typing import Set
from peewee import DoesNotExist
from exceptions.NoAliasFoundError import NoAliasFoundError
from persistence import helper_ip_address, helper_domain_name
from persistence.BaseModel import DomainNameEntity, AliasAssociation, IpAddressEntity
from utils import list_utils


def insert(dne: DomainNameEntity, adne: DomainNameEntity) -> AliasAssociation:
    aa, created = AliasAssociation.get_or_create(name=dne, alias=adne)
    return aa


def get_alias_from_entity(dne: DomainNameEntity) -> DomainNameEntity:
    query = AliasAssociation.select() \
        .join(DomainNameEntity, on=(AliasAssociation.name == dne))
    for row in query:
        return row.alias
    raise NoAliasFoundError(dne.name)


def get_alias_from_name(domain_name: str) -> DomainNameEntity:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    query = AliasAssociation.select() \
        .join(DomainNameEntity, on=(AliasAssociation.name == dne))
    for row in query:
        return row.alias
    raise NoAliasFoundError(domain_name)


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
