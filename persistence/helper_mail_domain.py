from typing import Set
from peewee import DoesNotExist
from entities.DomainName import DomainName
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_domain_name
from persistence.BaseModel import MailDomainEntity, MailServerEntity, MailDomainComposedAssociation


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


def get_every_of(mse: MailServerEntity) -> Set[MailDomainEntity]:
    query = MailDomainComposedAssociation.select()\
        .where(MailDomainComposedAssociation.mail_server == mse)
    result = set()
    for row in query:
        result.add(row.mail_domain)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result



def get_everyone() -> Set[MailDomainEntity]:
    query = MailDomainEntity.select()
    result = set()
    for row in query:
        result.add(row)
    return result
