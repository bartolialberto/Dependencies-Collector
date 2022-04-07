from typing import Set
from peewee import DoesNotExist
from entities.DomainName import DomainName
from entities.Url import Url
from persistence import helper_web_site, helper_domain_name
from persistence.BaseModel import WebSiteEntity, DomainNameEntity, WebSiteDomainNameAssociation


def insert(wse: WebSiteEntity, dne: DomainNameEntity) -> WebSiteDomainNameAssociation:
    wsdna, created = WebSiteDomainNameAssociation.get_or_create(web_site=wse, domain_name=dne)
    return wsdna


def get_from_entity_web_site(wse: WebSiteEntity) -> WebSiteDomainNameAssociation:
    try:
        wsdna = WebSiteDomainNameAssociation.get(WebSiteDomainNameAssociation.web_site == wse)
    except DoesNotExist:
        raise
    return wsdna


def get_from_entity_domain_name(dne: DomainNameEntity) -> Set[WebSiteDomainNameAssociation]:
    query = WebSiteDomainNameAssociation.select()\
        .where(WebSiteDomainNameAssociation.domain_name == dne)
    result = set()
    for row in query:
        result.add(row)
    return result

