from typing import List, Tuple, Set
from peewee import DoesNotExist
from persistence import helper_web_site, helper_domain_name
from persistence.BaseModel import WebServerEntity, WebSiteEntity, WebSiteLandsAssociation, DomainNameEntity


def insert(name: str) -> Tuple[WebServerEntity, DomainNameEntity]:
    dne = helper_domain_name.insert(name)
    wse, created = WebServerEntity.get_or_create(name=dne)
    return wse, dne


def get(name: str) -> Tuple[WebServerEntity, DomainNameEntity]:
    try:
        dne = helper_domain_name.get(name)
    except DoesNotExist:
        raise
    try:
        wse = WebServerEntity.get(WebServerEntity.name == dne)
    except DoesNotExist:
        raise
    return wse, dne


def get_from_entity_web_site(wse: WebSiteEntity) -> Set[WebServerEntity]:
    query = WebSiteLandsAssociation.select() \
        .where((WebSiteLandsAssociation.web_site == wse) & (WebSiteLandsAssociation.web_server.is_null(False)))
    result = set()
    for row in query:
        result.add(row.web_server)
    return result


def get_from_entity_web_site_and_scheme(wse: WebSiteEntity, https: bool) -> Set[WebServerEntity]:
    query = WebSiteLandsAssociation.select() \
        .where((WebSiteLandsAssociation.web_site == wse) & (WebSiteLandsAssociation.https == https) & (WebSiteLandsAssociation.web_server.is_null(False)))
    result = set()
    for row in query:
        result.add(row.web_server)
    return result


def get_from_web_site_and_scheme(website_param: str or WebSiteEntity, https: bool, first_only: bool) -> List[WebServerEntity] or WebServerEntity:
    wse = None
    query = None
    if isinstance(website_param, WebSiteEntity):
        wse = website_param
    else:
        try:
            wse = helper_web_site.get(website_param)
        except DoesNotExist:
            raise
    if first_only:
        query = WebSiteLandsAssociation.select() \
            .where((WebSiteLandsAssociation.web_site == wse) & (WebSiteLandsAssociation.https == https) & (WebSiteLandsAssociation.web_server.is_null(False)))\
            .limit(1)
        for row in query:
            return row.web_server
        raise DoesNotExist
    else:
        query = WebSiteLandsAssociation.select()\
            .where((WebSiteLandsAssociation.web_site == wse) & (WebSiteLandsAssociation.https == https) & (WebSiteLandsAssociation.web_server.is_null(False)))
        result = list()
        for row in query:
            result.append(row.web_server)
        return result


def get_everyone() -> Set[WebServerEntity]:
    query = WebServerEntity.select()
    result = set()
    for row in query:
        result.add(row)
    return result
