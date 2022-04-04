from typing import Set

from peewee import DoesNotExist

from persistence.BaseModel import MailDomainEntity, MailDomainComposedAssociation, MailServerEntity


def insert(mde: MailDomainEntity, mse: MailServerEntity or None) -> MailDomainComposedAssociation:
    mdca, created = MailDomainComposedAssociation.get_or_create(mail_domain=mde, mail_server=mse)
    return mdca


def get_of_entity_mail_domain(mde: MailDomainEntity) -> Set[MailDomainComposedAssociation]:
    query = MailDomainComposedAssociation.select()\
        .where(MailDomainComposedAssociation.mail_domain == mde)
    result = set()
    for row in query:
        result.add(row)
    return result


def get_unresolved() -> Set[MailDomainComposedAssociation]:
    query = MailDomainComposedAssociation.select()\
        .where(MailDomainComposedAssociation.mail_server.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
