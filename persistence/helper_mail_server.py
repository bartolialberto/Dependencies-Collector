from typing import Set
from peewee import DoesNotExist
from entities.DomainName import DomainName
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_domain_name, helper_ip_address
from persistence.BaseModel import MailServerEntity, MailDomainEntity, MailDomainComposedAssociation, IpAddressEntity, \
    DomainNameEntity


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


def get_every_of(mde: MailDomainEntity) -> Set[MailServerEntity]:
    query = MailDomainComposedAssociation.select()\
        .where((MailDomainComposedAssociation.mail_domain == mde) & (MailDomainComposedAssociation.mail_server.is_null(False)))
    result = set()
    for row in query:
        result.add(row.mail_server)
    return result


def filter_domain_names(dnes: Set[DomainNameEntity]) -> Set[MailServerEntity]:
    query = MailServerEntity.select()\
        .where(MailServerEntity.name.in_(dnes))
    result = set()
    for row in query:
        result.add(row)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result


def get_everyone() -> Set[MailServerEntity]:
    query = MailServerEntity.select()
    result = set()
    for row in query:
        result.add(row)
    return result
