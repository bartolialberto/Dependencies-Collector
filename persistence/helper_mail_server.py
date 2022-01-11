from typing import Tuple
from persistence import helper_domain_name
from persistence.BaseModel import MailServerEntity, DomainNameEntity


def insert(mailserver: str) -> Tuple[MailServerEntity, DomainNameEntity]:
    dne = helper_domain_name.insert(mailserver)
    nse, created = MailServerEntity.get_or_create(name=dne)
    return nse, dne

