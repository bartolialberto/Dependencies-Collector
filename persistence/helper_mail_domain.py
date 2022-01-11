from typing import Tuple
from persistence import helper_domain_name
from persistence.BaseModel import DomainNameEntity, MailDomainEntity


def insert(mail_domain: str) -> Tuple[MailDomainEntity, DomainNameEntity]:
    dne = helper_domain_name.insert(mail_domain)
    nse, created = MailDomainEntity.get_or_create(name=dne)
    return nse, dne

