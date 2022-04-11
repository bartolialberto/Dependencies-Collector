from persistence.BaseModel import WebSiteEntity, DomainNameEntity, WebSiteDomainNameAssociation


def insert(wse: WebSiteEntity, dne: DomainNameEntity) -> WebSiteDomainNameAssociation:
    wsdna, created = WebSiteDomainNameAssociation.get_or_create(web_site=wse, domain_name=dne)
    return wsdna
