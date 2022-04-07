from typing import Tuple, Set
from peewee import DoesNotExist

from entities.DomainName import DomainName
from persistence import helper_domain_name, helper_mail_server
from persistence.BaseModel import DomainNameEntity, MailDomainEntity, MailServerEntity, MailDomainComposedAssociation


def insert(mail_domain: DomainName) -> MailDomainEntity:
    dne = helper_domain_name.insert(mail_domain)
    nse, created = MailDomainEntity.get_or_create(name=dne)
    return nse


def get(mail_domain: DomainName) -> MailDomainEntity:
    try:
        dne = helper_domain_name.get(mail_domain)
    except DoesNotExist:
        raise
    try:
        return MailDomainEntity.get(MailDomainEntity.name == dne)
    except DoesNotExist:
        raise


def get_everyone() -> Set[MailDomainEntity]:
    query = MailDomainEntity.select()
    result = set()
    for row in query:
        result.add(row)
    return result
