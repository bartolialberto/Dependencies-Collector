from persistence.BaseModel import MailDomainEntity, MailDomainComposedAssociation, MailServerEntity


def insert(mde: MailDomainEntity, mse: MailServerEntity) -> MailDomainComposedAssociation:
    mdca, created = MailDomainComposedAssociation.get_or_create(mail_domain=mde, mail_server=mse)
    return mdca
