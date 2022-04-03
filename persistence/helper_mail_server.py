from typing import Tuple, Set
from peewee import DoesNotExist

from entities.DomainName import DomainName
from persistence import helper_domain_name, helper_mail_domain
from persistence.BaseModel import MailServerEntity, DomainNameEntity, MailDomainEntity, MailDomainComposedAssociation


def insert(mailserver: DomainName) -> MailServerEntity:
    dne = helper_domain_name.insert(mailserver)
    nse, created = MailServerEntity.get_or_create(name=dne)
    return nse


def get(mail_server: DomainName) -> MailServerEntity:
    try:
        dne = helper_domain_name.get(mail_server)
    except DoesNotExist:
        raise
    try:
        return MailServerEntity.get(MailServerEntity.name == dne)
    except DoesNotExist:
        raise


def get_every_of(mail_domain_parameter: MailDomainEntity or str) -> Set[MailServerEntity]:
    mde = None
    if isinstance(mail_domain_parameter, MailDomainEntity):
        mde = mail_domain_parameter
    else:
        try:
            mde = helper_mail_domain.get(mail_domain_parameter)
        except DoesNotExist:
            raise
    query = MailDomainComposedAssociation.select()\
        .where((MailDomainComposedAssociation.mail_domain == mde) & (MailDomainComposedAssociation.mail_server.is_null(False)))
    result = set()
    for row in query:
        result.add(row.mail_server)
    return result


def get_everyone() -> Set[MailServerEntity]:
    query = MailServerEntity.select()
    result = set()
    for row in query:
        result.add(row)
    return result
