from typing import List
from peewee import DoesNotExist
from persistence.BaseModel import DomainNameEntity, AliasAssociation
from utils import list_utils


def insert(dne: DomainNameEntity, adne: DomainNameEntity) -> AliasAssociation:
    aa, created = AliasAssociation.get_or_create(name=dne, alias=adne)
    return aa


# TODO: da testare
def get_all_aliases_from_name(domain_name: str) -> List[DomainNameEntity]:
    try:
        dne = DomainNameEntity.get(DomainNameEntity.name == domain_name)
    except DoesNotExist:
        raise
    result = list()
    query = AliasAssociation.select()\
        .join_from(AliasAssociation, DomainNameEntity, on=(AliasAssociation.name == DomainNameEntity.name))\
        .where(AliasAssociation.name == dne)
    for row in query:
        result.append(row.alias)
    query = AliasAssociation.select()\
        .join_from(AliasAssociation, DomainNameEntity, on=(AliasAssociation.alias == DomainNameEntity.name))\
        .where(AliasAssociation.alias == dne)
    for row in query:
        list_utils.append_with_no_duplicates(result, row.name)
    return result
