from typing import Set
from persistence.BaseModel import MailDomainEntity, MailDomainComposedAssociation, MailServerEntity


def insert(mde: MailDomainEntity, mse: MailServerEntity or None) -> MailDomainComposedAssociation:
    mdca, created = MailDomainComposedAssociation.get_or_create(mail_domain=mde, mail_server=mse)
    return mdca


def get_unresolved() -> Set[MailDomainComposedAssociation]:
    query = MailDomainComposedAssociation.select()
    result = set()
    for row in query:
        result.add(row)
    return result
