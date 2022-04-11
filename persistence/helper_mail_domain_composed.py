from typing import Set, List, Union, Dict
from persistence.BaseModel import MailDomainEntity, MailDomainComposedAssociation, MailServerEntity


def insert(mde: MailDomainEntity, mse: MailServerEntity or None) -> MailDomainComposedAssociation:
    mdca, created = MailDomainComposedAssociation.get_or_create(mail_domain=mde, mail_server=mse)
    return mdca


def bulk_inserts(data_source: List[Dict[str, Union[MailDomainEntity, MailServerEntity, None]]]) -> None:
    MailDomainComposedAssociation.insert_many(data_source).on_conflict_replace().execute()


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
