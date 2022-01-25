from typing import Tuple, Set
from peewee import DoesNotExist
from persistence import helper_domain_name, helper_mail_server
from persistence.BaseModel import DomainNameEntity, MailDomainEntity, MailServerEntity, MailDomainComposedAssociation


def insert(mail_domain: str) -> Tuple[MailDomainEntity, DomainNameEntity]:
    dne = helper_domain_name.insert(mail_domain)
    nse, created = MailDomainEntity.get_or_create(name=dne)
    return nse, dne


def get(mail_domain_parameter: MailDomainEntity or str) -> MailDomainEntity:
    dne = None
    if isinstance(mail_domain_parameter, DomainNameEntity):
        dne = mail_domain_parameter
    else:
        try:
            dne = helper_domain_name.get(mail_domain_parameter)
        except DoesNotExist:
            raise
    try:
        return MailDomainEntity.get(MailDomainEntity.name == dne)
    except DoesNotExist:
        raise


def get_every_of(mail_server_parameter: MailServerEntity or str) -> Set[MailDomainEntity]:
    mse = None
    if isinstance(mail_server_parameter, MailServerEntity):
        mse = mail_server_parameter
    else:
        try:
            mse = helper_mail_server.get(mail_server_parameter)
        except DoesNotExist:
            raise
    query = MailDomainComposedAssociation.select()\
        .where(MailDomainComposedAssociation.mail_server == mse)
    result = set()
    for row in query:
        result.add(row.mail_domain)
    return result
