from peewee import DoesNotExist
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from persistence.BaseModel import DomainNameEntity
from utils import domain_name_utils


def insert(string: str) -> DomainNameEntity:
    try:
        domain_name_utils.grammatically_correct(string)
    except InvalidDomainNameError:
        raise
    dne, created = DomainNameEntity.get_or_create(name=string)
    return dne


def get(domain_name: str) -> DomainNameEntity:
    try:
        return DomainNameEntity.get_by_id(domain_name)
    except DoesNotExist:
        raise
